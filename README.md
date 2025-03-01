# ASIL-Gen: Automotive Scenario Generation and ASIL Classification Toolkit

A toolkit for generating automotive scenarios, evaluating their safety levels (ASIL), and comparing optimization algorithms (NSGA-II vs. Random Search) for scenario selection.

---

## Overview

This repository contains tools for:
1. Generating variations of driving scenarios
2. Executing scenarios in CARLA simulator
3. Selecting critical scenarios using NSGA and Random Search algorithms
4. Determining Automotive Safety Integrity Levels (ASIL) of selected scenarios
5. Analyzing results with statistical methods

---

## Prerequisites

1. **CARLA Simulator**:  
   Install CARLA from [carla-simulator/carla](https://github.com/carla-simulator/carla).  
2. **Scenario Runner**:  
   Install the CARLA Scenario Runner from [carla-simulator/scenario_runner](https://github.com/carla-simulator/scenario_runner).  

---

## Setup

1. **Clone this repository**:  
   ```bash
   git clone https://github.com/Fizza129/ASIL-Gen.git
   ```

2. **Install Python dependencies** (if required):  
   Ensure `numpy`, `pandas`, `deap` (for NSGA-II), and other standard libraries are installed.  

---

## Usage

### 1. Running Scenarios
- **Pre-generated Scenarios**:  
  - Extract `Scenario Dataset/Scenario_Dataset_1-4.zip`.  
  - Copy `.py` scenario files to `scenario_runner/srunner/scenarios/`.  
  - Copy `.xml` configuration files to `scenario_runner/srunner/examples/`.  
  - Follow [Scenario Runner documentation](https://github.com/carla-simulator/scenario_runner) to execute scenarios.  

- **Custom Scenarios**:  
  Use scripts in `Scenario Generation Scripts/` to generate new variations. Example:  
  ```bash
  python script_change_lane.py  # Generates new lane-change variations
  ```

### 2. Scenario Selection
- **NSGA-II Optimization**:  
  Run scripts in the `NSGA/` folder on scenario execution results:  
  ```bash
  python "NSGA/NSGA_choice.py"
  ```
- **Random Search**:  
  Execute scripts in the `Random Search/` folder:  
  ```bash
  python "Random Search/random_search_choice.py"
  ```
  The selected scenarios will be saved in JSON format.

### 3. ASIL Classification
- Use scripts in the `ASIL/` folder to compute ASIL levels (A/B/C/D/QM) for selected scenarios:  
  ```bash
  python "ASIL/ASIL.py"  # Calculates ASIL levels
  ```
  ```bash
  python "ASIL/ASIL_percentages.py"  # Calculates ASIL distribution percentages
  ```

### 4. Statistical Comparison (NSGA vs. Random Search)
- Run Mann-Whitney U Test scripts in `Mann Whitney Test/`:  
  ```bash
  python "Mann Whitney Test/Mann Whitney and Effect Size.py"
  ```

---

## Repository Structure

```
ASIL-Gen/  
├── ASIL/                  # ASIL classification and percentage calculation  
├── Mann Whitney Test/     # Statistical tests for comparing NSGA and Random Search  
├── NSGA/                  # NSGA-II optimization for scenario selection  
├── Random Search/         # Random Search-based scenario selection  
├── Scenario Dataset/      # Pre-generated scenario variations (Python + XML)  
├── Scenario Generation Scripts/  # Scripts to generate new scenario variations  
└── Scenario Results/      # Output results (e.g., Scenario Results.zip)  
```

---

## Scenario Types

The repository contains 13 unique scenarios:
- Lane change
- Cut-in with static vehicle
- Dynamic object crossing
- Following leading vehicle
- Following leading vehicle with obstacle
- Hazard at side lane
- No signal junction crossing
- Opposite vehicle running red light
- Other leading vehicle
- Parked obstacle
- Parking crossing pedestrian
- Vehicle opens door
- Vehicle turning right

---

## Results

The `Scenario Results` folder contains the outputs from executed scenarios.

---

## Notes
- **Dataset Usage**: The `Scenario Dataset` contains 1,000 variations for each unique scenario. Extract and copy files as instructed.  
- **Custom Generation**: Modify scripts in `Scenario Generation Scripts/` to create new scenario variations.  

---
