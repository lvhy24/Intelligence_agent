from langchain_community.chat_models import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
import pandas as pd
from math import radians, sin, cos, sqrt, atan2
import asyncio, json, os
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trajectory_generation.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TrajectoryGenerator")

df = pd.read_csv("C:\\Users\\Lenovo\\Desktop\\beijing_pois_combined.csv")
residents = pd.read_csv("C:\\Users\\Lenovo\\Desktop\\residents_100.csv")
llm = ChatTongyi(model="qwen-max-latest", temperature=0.3, dashscope_api_key="sk-d312dfc545954504b1b8d5ef7cf2dad1")
system_template = "你是一个模拟北京居民日常出行的轨迹生成助手。请根据用户的属性生成合理且符合逻辑的一天行程轨迹。"
human_template = open("C:\\Users\\Lenovo\\Desktop\\prompt_template.txt", encoding="utf-8").read()
prompt = ChatPromptTemplate.from_messages([
    ("system", system_template),
    ("human", human_template)
])

# 计算两点之间的地理距离（公里）
def haversine_distance(coord1, coord2):
    # 计算两点之间的大圆距离（Haversine公式）
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # Haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    r = 6371  # 地球平均半径，单位为公里
    return c * r

def get_nearby_pois(home_coord, max_distance=10):
    """获取指定坐标10公里范围内的POI"""
    logger.info(f"正在查找坐标 {home_coord} 附近 {max_distance} 公里内的POI")
    nearby_pois = []
    home_lon, home_lat = map(float, home_coord.split(','))
    
    for _, poi in df.iterrows():
        poi_lon, poi_lat = map(float, poi['location'].split(','))
        distance = haversine_distance((home_lat, home_lon), (poi_lat, poi_lon))
        
        if distance <= max_distance:
            nearby_pois.append(poi)
    
    logger.info(f"找到 {len(nearby_pois)} 个附近POI")
    return pd.DataFrame(nearby_pois)

def generate_trajectory(resident):
    logger.info(f"开始为居民 {resident['id']} 生成轨迹 (年龄: {resident['age']}, 职业: {resident['occupation']})")
    # 获取家庭坐标附近的POI
    nearby_pois = get_nearby_pois(resident['home'])
    
    # 构建POI字符串
    poi_str = ",".join([f"{r['name']}" for _, r in nearby_pois.iterrows()])
    
    messages = prompt.format_messages(
        age=resident['age'], occupation=resident['occupation'], 
        budget_level=resident['budget_level'], family_role=resident['family_role'],
        home=resident['home'], poi_list=poi_str[:5000]
    )
    logger.debug(f"POI字符串长度: {len(poi_str)}")
    
    try:
        logger.info("调用大语言模型生成轨迹...")
        result = llm.invoke(messages).content
        logger.info(f"居民 {resident['id']} 的轨迹生成成功")
        return result
    except Exception as e:
        logger.error(f"生成居民 {resident['id']} 轨迹时出错: {str(e)}")
        raise

async def run_all():
    logger.info(f"开始处理 {len(residents)} 名居民的轨迹生成任务")
    results = []
    for _, r in residents.iterrows():
        cache_file = f"traj_{r['id']}.json"
        if os.path.exists(cache_file): 
            logger.info(f"居民 {r['id']} 的轨迹已存在，从缓存加载")
            with open(cache_file, "r", encoding="utf-8") as f:
                traj = json.load(f)
        else:
            logger.info(f"居民 {r['id']} 的轨迹不存在，开始生成")
            traj = generate_trajectory(r)
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(traj, f, ensure_ascii=False, indent=2)
            logger.info(f"居民 {r['id']} 的轨迹已保存到 {cache_file}")
        results.append({'id': r['id'], 'trajectory': traj})
    logger.info(f"所有居民轨迹处理完成，共 {len(results)} 条")
    return results

if __name__ == "__main__":
    try:
        logger.info("轨迹生成程序启动")
        trajectories = asyncio.run(run_all())
        # 保存所有轨迹到一个文件
        with open("trajectories.json", 'w', encoding='utf-8') as f:
            json.dump(trajectories, f, ensure_ascii=False, indent=2)
        logger.info(f"所有轨迹已保存到 trajectories.json，程序执行完成")
    except Exception as e:
        logger.critical(f"程序执行过程中发生严重错误: {str(e)}")
        raise