import os, json, time, hashlib, pathlib
CACHE_DIR = pathlib.Path("cache_hours")
CACHE_DIR.mkdir(exist_ok=True)
import certifi, ssl
os.environ["REQUESTS_CA_BUNDLE"]  = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context
import requests, time, pandas as pd

DETAIL_URL = "https://restapi.amap.com/v3/place/detail"

def get_business_hours(poi_id: str) -> str:
    """
    带本地缓存 + 限速的营业时间抓取
    返回字符串，失败返回空串
    """
    # 1. 本地缓存文件名
    cache_file = CACHE_DIR / f"{poi_id}.json"

    # 2. 命中缓存直接返回
    if cache_file.exists():
        return json.load(cache_file.open(encoding="utf-8"))

    # 3. 限速：每次调用间隔 1.5 秒
    time.sleep(1.5)

    # 4. 请求
    params = {"key": KEY, "id": poi_id}
    try:
        resp = requests.get(DETAIL_URL, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # 5. 提取营业时间
        hours = (
            data.get("pois", [{}])[0]
                .get("business", {})
                .get("business_hours", "")
        )

        # 6. 写入缓存
        json.dump(hours, cache_file.open("w", encoding="utf-8"))
        return hours
    except Exception as e:
        # 出错也写空串，避免反复尝试
        json.dump("", cache_file.open("w", encoding="utf-8"))
        return ""
KEY = "40d659fde3776f8e3ad8e2aea3e4e4d9"             
CITY = "北京"
TYPES = {
    "商场": "购物中心",
    "住宅区": "小区",
    "写字楼":"",
    "学校": "大学",
    "餐馆": "餐厅",
    "银行": "银行",
    "酒店": "酒店",
    "药店": "药店",
}
URL = "https://restapi.amap.com/v3/place/text"

def fetch_one(keyword, page=1, offset=25):
    params = {
        "key": KEY,
        "keywords": keyword,
        "city": CITY,
        "citylimit": "true",
        "offset": offset,
        "page": page,
        "output": "json"
    }
    r = requests.get(URL, params=params, timeout=10)
    data = r.json()
    if data["status"] == "1":
        return data["pois"]
    return []

def fetch_all(keyword):
    pois, page = [], 1
    while True:
        batch = fetch_one(keyword, page)
        if not batch or page > 20:      # 最多 20 页（500条）防止超限
            break
        pois.extend(batch)
        page += 1
        time.sleep(0.2)                 # 限速
    return pois

# 3. 主流程：抓取 + 合并
all_records = []
for label, kw in TYPES.items():
    print(f"正在抓取 {label} ...")
    raw = fetch_all(kw)
    # 只要关键字段
    for p in raw:
        biz_hours = get_business_hours(p["id"])
        all_records.append({
            "name": p["name"],
            "type": label,                    # 商场/地铁站/住宅区
            "location": p["location"],        # "116.123,39.456"
            "address": p.get("address", ""),
            "open_time": biz_hours
        })
        time.sleep(1)  # 限速

df = pd.DataFrame(all_records)
df.drop_duplicates(subset=["name", "location"], inplace=True)
df.to_csv("beijing_pois.csv", index=False, encoding="utf-8-sig")
print("已保存 beijing_pois.csv，共", len(df), "条")