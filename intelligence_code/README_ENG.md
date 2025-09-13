# Beijing Resident Daily Travel Trajectory Generation System

## Overview
This system is a Large Language Model (LLM) based simulator for generating daily travel trajectories of Beijing residents. It integrates resident attributes (age, occupation, family status, budget, etc.) and Beijing POI (Point of Interest) data to produce logical and personalized daily travel trajectories. It also supports quality assessment of the generated trajectories.

## System Workflow
#### Data Preparation:
Collects Beijing POI data and generates simulated resident attribute data.
#### Trajectory Generation:
Uses LLM to generate personalized travel trajectories based on resident attributes and nearby POIs.
#### Trajectory Evaluation:
Evaluates the quality of the generated trajectories from three dimensions: visit distribution (KL divergence), movement radius, and trip chain length.
#### File Description:
- `agent.py` - Main program, responsible for loading data and generating resident trajectories.
- `evaluate.py` - Evaluation script, calculates various metrics for the generated trajectories.
- `get_beijing_poi.py` - POI data collection script (fetches data from the Amap API).
- `get_user.py` - User data generation script.
- `prompt_template.txt` - LLM prompt template.
- `beijing_pois_combined.csv - Data for all POI
- `residents_100.csv` - Attribute data for 100 simulated residents.
- `trajectories.json` - Pre-generated trajectory results file.

## Detailed Instructions
#### 1. Environment Setup
Ensure the following Python libraries are installed:
```bash
pip install langchain-community langchain-core pandas requests scipy
```
#### 2. Obtain POI Data
To update the POI data, run:
```bash
python get_beijing_poi.py
```
This will call the Amap API to retrieve various categories of POIs in Beijing and save them to beijing_pois_combined.csv.
To generate the user data,run:
```bash
python get_user.py
```
This will generate attribute data for 100 simulated users and save it to residents_100.csv.
#### 3. Generate Resident Trajectories
Run the main program:
```bash
python agent.py
```
The program will:
Read resident attributes (residents_100.csv)
Call the Tongyi Qianwen model to generate personalized trajectories
Save each resident's trajectory to a separate JSON file (traj_<id>.json)
Aggregate all trajectories into trajectories.json
#### 4. Evaluate Generated Trajectories
Run the evaluation script:
```bash
python evaluate.py
```
Evaluation metrics include:
Visit Distribution KL Divergence: Compares the difference between the generated trajectory distribution and the real POI visit distribution.
Average Movement Radius: The maximum daily activity range of a resident (in kilometers).
Average Trip Chain Length: The number of POIs in a trajectory.
## Notes
The Tongyi Qianwen API key (dashscope_api_key) needs to be configured.
File paths may need adjustment based on the actual environment.
The POI data collection script includes API call rate limits (1 call per 1.5 seconds).
#### Result Example
The output file trajectories.json contains the trajectories for each resident, formatted as follows:
```json
[
  {"id": 1, "trajectory": "[POI1, POI2, ...]"},
  ...
]
```