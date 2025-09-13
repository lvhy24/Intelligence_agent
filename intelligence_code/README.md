# 北京居民日常出行轨迹生成系统
## 概述
该系统是一个基于大语言模型（LLM）的北京居民日常出行轨迹模拟器。它结合居民属性（年龄、职业、家庭状况，预算等）和北京POI（兴趣点）数据，生成符合逻辑且个性化的日常出行轨迹，并支持对生成轨迹的质量评估。
## 系统运行流程
#### 数据准备：
采集北京POI数据与生成模拟居民属性数据
#### 轨迹生成：
基于居民属性与附近POI，使用LLM生成个性化出行轨迹
#### 轨迹评估：
从访问分布（KL散度）、移动半径和出行链长度三个维度评估生成轨迹的质量
#### 文件说明：
agent.py - 主程序，负责加载数据、生成居民轨迹
evaluate.py - 评估脚本，计算生成轨迹的各项指标
get_beijing_poi.py - POI数据采集脚本（从高德地图API获取）
get_user.py - 用户数据生成脚本
prompt_template.txt - LLM提示词模板
beijing_pois_combined.csv - 采集到的所有POI数据
residents_100.csv - 100个模拟居民属性数据
trajectories.json - 已生成的轨迹结果文件
## 详细操作步骤
#### 1. 环境配置，确保安装以下Python库：
```bash
pip install langchain-community langchain-core pandas requests scipy
```
#### 2. 获取POI数据和模拟用户数据
若需更新POI数据，运行：
```bash
python get_beijing_poi.py
```
这将调用高德地图API，获取北京各类POI并保存至beijing_pois_combined.csv
若需生成用户数据用于模拟，运行：
```bash
python get_user.py
```
这将生成100个模拟用户的属性数据，并保存至residents_100.csv
#### 3. 生成居民轨迹
运行主程序：
```bash
python agent.py
```
程序将：
读取居民属性（residents_100.csv）
调用通义千问模型生成个性化轨迹
保存每个居民的轨迹至单独JSON文件（traj_<id>.json）
汇总所有轨迹至trajectories.json
#### 4. 评估生成轨迹
运行评估脚本：
```bash
python evaluate.py
```
评估指标包括：
访问分布KL散度：比较生成轨迹与真实POI访问分布的差异
平均移动半径：居民一天内的最大活动范围（公里）
平均出行链长度：轨迹中POI的数量
## 注意事项
需配置通义千问API密钥（dashscope_api_key）
文件路径需根据实际环境调整
POI数据采集脚本含API调用频次限制（1.5秒/次）
#### 结果示例
输出文件trajectories.json包含每个居民的轨迹，格式如下：
```json
[
  {"id": 1, "trajectory": "[POI1, POI2, ...]"},
  ...
]
```