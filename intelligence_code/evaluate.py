from scipy.stats import entropy
from math import radians, sin, cos, sqrt, atan2
import numpy as np
import json
import re
import pandas as pd
import logging  # 新增日志模块

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("trajectory_evaluation.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TrajectoryEvaluator")

#from agent import trajectories
logger.info("开始加载轨迹数据...")
with open("C:\\Users\\Lenovo\\Desktop\\trajectories.json","r",encoding="utf-8") as f:
    trajectories=json.load(f)
logger.info(f"成功加载 {len(trajectories)} 条轨迹数据")

logger.info("开始加载POI数据...")
df=pd.read_csv("C:\\Users\\Lenovo\\Desktop\\beijing_pois_combined.csv")
logger.info(f"成功加载 {len(df)} 条POI数据")

logger.info("开始加载居民数据...")
residents=pd.read_csv("C:\\Users\\Lenovo\\Desktop\\residents_100.csv")
logger.info(f"成功加载 {len(residents)} 条居民数据")

# 解析轨迹
def parse_unquoted_list_string(s):
    """
    解析无引号的列表字符串，例如: "[华腾园,敬业科技产业园,天坛公园]"
    """
    # 移除方括号和空格
    s = s.strip().strip('[]').strip()
    
    # 按逗号分割并移除每个元素周围的空格
    if s:  # 确保字符串不为空
        return [item.strip() for item in s.split(',')]
    else:
        return []

def parse_traj(t):
    logger.debug(f"解析轨迹: {str(t)[:100]}...")  # 只记录前100个字符避免日志过大
    if isinstance(t, str):
        # 移除 Markdown 代码块标记
        t = re.sub(r'^```json\s*|\s*```$', '', t, flags=re.MULTILINE)
        # 移除多余空格和换行
        t = t.strip()
    
    # 解析 JSON
    try:
        steps = json.loads(t) if isinstance(t, str) else t
        logger.debug("使用JSON解析成功")
    except json.JSONDecodeError:
        # 如果JSON解析失败，尝试无引号格式
        logger.debug("JSON解析失败，尝试无引号格式")
        steps = parse_unquoted_list_string(t) if isinstance(t, str) else []
    
    logger.debug(f"解析结果: {len(steps)} 个地点")
    return steps

# 在读取df后，创建一个映射字典
logger.info("创建POI名称到类型的映射字典...")
name_to_type = dict(zip(df['name'], df['type']))
def get_poi_type(poi_name):
    poi_type = name_to_type.get(poi_name, "其他")
    logger.debug(f"POI '{poi_name}' 的类型为: {poi_type}")
    return poi_type
    
# 1. 访问分布KL散度
logger.info("开始计算访问分布KL散度...")
real_dist = {'写字楼':0.437, '商场':0.211, '住宅区':0.297, '其他':0.055}
logger.info(f"真实分布: {real_dist}")

sim_pois = [get_poi_type(step) for t in trajectories for step in parse_traj(t['trajectory'])]
logger.info(f"从轨迹中提取了 {len(sim_pois)} 个POI访问记录")

sim_dist = pd.Series(sim_pois).value_counts(normalize=True).reindex(real_dist.keys(), fill_value=0)
logger.info(f"模拟分布: {sim_dist.to_dict()}")

kl_div = entropy(sim_dist, pd.Series(real_dist))
logger.info(f"KL散度计算结果: {kl_div}")

# 2. 移动半径
logger.info("开始计算移动半径...")
name_to_loc=dict(zip(df['name'], df['location']))
logger.info("创建POI名称到位置的映射字典...")

def get_poi_loc(poi_name)->str:
    loc = name_to_loc.get(poi_name, "116.3,40.1")
    logger.debug(f"POI '{poi_name}' 的位置为: {loc}")
    return loc

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

def calc_radius(traj):
    logger.debug(f"计算轨迹的移动半径: {traj}")
    coords = [tuple(map(float, get_poi_loc(step).split(','))) for step in traj if ',' in get_poi_loc(step)]
    logger.debug(f"提取到 {len(coords)} 个有效坐标")
    
    if len(coords) < 2: 
        logger.debug("坐标数量不足，返回半径为0")
        return 0
        
    max_distance = max([haversine_distance(c1,c2) for c1 in coords for c2 in coords])
    logger.debug(f"最大距离(半径): {max_distance} 公里")
    return max_distance

logger.info("计算所有轨迹的移动半径...")
radii = []
for i, t in enumerate(trajectories):
    logger.info(f"计算第 {i+1}/{len(trajectories)} 条轨迹的移动半径")
    radius = calc_radius(parse_traj(t['trajectory']))
    radii.append(radius)
    logger.info(f"轨迹 {i+1} 的移动半径: {radius} 公里")

def get_ave_radii(radii)->float:
    init=0
    for item in radii:
        init+=item
    result = init/len(radii)
    logger.info(f"平均移动半径计算结果: {result} 公里")
    return result

# 3. 出行链长度
logger.info("开始计算出行链长度...")
lengths = []
for i, t in enumerate(trajectories):
    length = len(parse_traj(t['trajectory']))
    lengths.append(length)
    logger.info(f"轨迹 {i+1} 的出行链长度: {length}")

def get_ave_len(lengths)->int:
    init=0
    for item in lengths:
        init+=item
    result = init/len(lengths)
    logger.info(f"平均出行链长度计算结果: {result}")
    return result

# 输出最终结果
logger.info("评估完成，输出最终结果:")
print(f"访问分布KL散度为：{kl_div}\n")
print(f"平均移动半径为：{get_ave_radii(radii)}\n")
print(f"平均出行链长度为：{get_ave_len(lengths)}\n")

logger.info("轨迹评估程序执行完成")