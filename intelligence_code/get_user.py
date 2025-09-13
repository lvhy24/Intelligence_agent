import pandas as pd, random
random.seed(42)
N = 100
df=pd.read_csv("C:\\Users\\Lenovo\\Desktop\\beijing_pois_combined.csv")
invalid_types=['商场','公园','医院','餐厅','银行','博物馆','药店','理发店','快递点','写字楼']
valid_locations = df[~df['type'].isin(invalid_types)]['location'].tolist()#过滤掉不适合作为家庭地址的地点
weights = pd.read_csv("C:\\Users\\Lenovo\\Desktop\\full_weights.csv")   # ← 刚才的 CSV
rows = []
for _ in range(N):
    row = weights.sample(1, weights=weights["weight"]).iloc[0]
    low, high = map(int, row["age_bracket"].split("-"))
    age = random.randint(low, high)
    home=random.choice(valid_locations)
    rows.append([
        len(rows)+1, age, row["gender"], row["occupation"],
        row["family_role"], row["budget_level"],home
    ])

residents = pd.DataFrame(rows, columns=["id","age","gender","occupation","family_role","budget_level","home"])
residents.to_csv("residents_100.csv", index=False)
print("✅ 已生成，共", len(residents), "条。")