import json
import numpy as np
from deap import base, creator, tools, algorithms
from util import save_metrics_to_json

def is_pedestrian_or_cyclist_collision(scenario):
    collision_type = scenario["Collision Type"]
    return "walker" in collision_type or "diamondback" in collision_type

def is_vehicle_collision(scenario):
    return not is_pedestrian_or_cyclist_collision(scenario)

def calculate_collision_probability(scenario):
    time_probability = 1 - (scenario["Time to Collision"] / 10)
    speed_probability = scenario["Speed at Collision"] / 32
    weather_probabilities = {"ClearNoon": 0.4, "ClearNight": 0.6, "HardRainNoon": 0.8, "HardRainNight": 1.0}
    weather_probability = weather_probabilities[scenario["Weather"]]
    probability = time_probability * speed_probability * weather_probability
    return probability

def calculate_diversity(scenarios):
    speed_values = np.array([s["Speed at Collision"] for s in scenarios])
    time_values = np.array([s["Time to Collision"] for s in scenarios])
    intensity_values = np.array([s["Intensity"] for s in scenarios])
    
    # Use standard deviation as a measure of diversity
    speed_diversity = np.std(speed_values)
    time_diversity = np.std(time_values)
    intensity_diversity = np.std(intensity_values)
    
    # Aggregate the standard deviations into a single diversity measure
    # Here, we assume equal weighting for each attribute's diversity
    combined_diversity_score = speed_diversity + time_diversity + intensity_diversity
    
    return combined_diversity_score

# Global Speed Ranges
very_low_speed_range = (0, 15)
low_speed_range = (15, 50)
medium_speed_range = (50, 115)

def convert_speed_mps_to_kph(speed_mps):
    # Conversion factor: 1 km/h = 0.27778 m/s
    return speed_mps * 3.6  # 1 m/s = 3.6 km/h

def determine_severity(collision_type, speed_kph):
    # Determine Severity
    if collision_type == 'Pedestrian':
        if very_low_speed_range[0] <= speed_kph < very_low_speed_range[1]:
            return 'S2'
        elif low_speed_range[0] <= speed_kph < low_speed_range[1] or medium_speed_range[0] <= speed_kph < medium_speed_range[1]:
            return 'S3'
    elif collision_type == 'NPC_VEHICLE':
        if very_low_speed_range[0] <= speed_kph < very_low_speed_range[1]:
            return 'S1'
        elif low_speed_range[0] <= speed_kph < low_speed_range[1]:
            return 'S2'
        elif medium_speed_range[0] <= speed_kph < medium_speed_range[1]:
            return 'S3'
    elif collision_type == 'Obstacle':
        return 'S0'
    return 'Severity Not Defined'

def determine_exposure(weather, speed_kph):
    # Determine Exposure based on Weather and Speed
    if (weather == 'HardRainNoon' or weather == 'HardRainNight') and medium_speed_range[0] <= speed_kph < medium_speed_range[1]:
        return 'E4'
    elif (weather == 'HardRainNoon' or weather == 'HardRainNight') and low_speed_range[0] <= speed_kph < low_speed_range[1]:
        return 'E3'
    elif (weather == 'HardRainNoon' or weather == 'HardRainNight') and very_low_speed_range[0] <= speed_kph < very_low_speed_range[1]:
        return 'E2'
    elif (weather == 'ClearNoon' or weather == 'ClearNight') and medium_speed_range[0] <= speed_kph < medium_speed_range[1]:
        return 'E3'
    elif (weather == 'ClearNoon' or weather == 'ClearNight') and low_speed_range[0] <= speed_kph < low_speed_range[1]:
        return 'E2'
    elif (weather == 'ClearNoon' or weather == 'ClearNight') and very_low_speed_range[0] <= speed_kph < very_low_speed_range[1]:
        return 'E1'
    else:
        return 'Exposure Not Defined'

def determine_asil(severity_class, exposure_class, controllability_class):
    # ASIL Determination based on Severity, Exposure, and Controllability
    if severity_class == 'S1' and exposure_class in ['E1', 'E2'] and controllability_class == 'C3':
        return 'QM'
    elif severity_class == 'S1' and exposure_class == 'E3' and controllability_class == 'C3':
        return 'ASIL A'
    elif severity_class == 'S1' and exposure_class == 'E4' and controllability_class == 'C3':
        return 'ASIL B'
    elif severity_class == 'S2' and exposure_class == 'E1' and controllability_class == 'C3':
        return 'QM'
    elif severity_class == 'S2' and exposure_class == 'E2' and controllability_class == 'C3':
        return 'ASIL A'
    elif severity_class == 'S2' and exposure_class == 'E3' and controllability_class == 'C3':
        return 'ASIL B'
    elif severity_class == 'S2' and exposure_class == 'E4' and controllability_class == 'C3':
        return 'ASIL C'
    elif severity_class == 'S3' and exposure_class == 'E1' and controllability_class == 'C3':
        return 'ASIL A'
    elif severity_class == 'S3' and exposure_class == 'E2' and controllability_class == 'C3':
        return 'ASIL B'
    elif severity_class == 'S3' and exposure_class == 'E3' and controllability_class == 'C3':
        return 'ASIL C'
    elif severity_class == 'S3' and exposure_class == 'E4' and controllability_class == 'C3':
        return 'ASIL D'
    else:
        return 'ASIL Not Defined'

# Define the problem object
creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0)) # Maximize probability and intensity, minimize (maximize negative) diversity
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

# Assume scenarios is your list of scenarios loaded from JSON
with open("./scenarios.json", 'r') as file:
    all_scenarios = json.load(file)

# Prepare a list to store the results
asil_results = []

for scenario in all_scenarios:
    # Extract necessary information from each scenario
    weather = scenario["Weather"]
    collision_type = scenario["Collision Type"]
    speed_mps = scenario["Speed at Collision"]

    # Check collision_type to decide between pedestrian, vehicle, or obstacle
    if "walker" in collision_type or "diamondback" in collision_type:
        collision_type = 'Pedestrian'
    elif "vehicle" in collision_type:
        collision_type = 'NPC_VEHICLE'
    else:
        collision_type = 'Obstacle'

    # Convert speed from m/s to kph
    speed_kph = convert_speed_mps_to_kph(speed_mps)

    # Determine Severity, Exposure, and ASIL classes
    severity_class = determine_severity(collision_type, speed_kph)
    exposure_class = determine_exposure(weather, speed_kph)
    controllability_class = 'C3'  # Assuming a default value; modify as needed
    asil_level = determine_asil(severity_class, exposure_class, controllability_class)

    # Append the results with ASIL level to the list
    scenario["ASIL Level"] = asil_level
    asil_results.append(scenario)

# Ask user for the ASIL level they are interested in
user_choice = input("Enter the ASIL level to filter (A, B, C, D, or QM): ")
asil_choice = f"ASIL {user_choice}" if user_choice in ['A', 'B', 'C', 'D'] else user_choice

# Filter scenarios based on the ASIL level
filtered_scenarios = [scenario for scenario in asil_results if scenario["ASIL Level"] == asil_choice]

# Save the filtered scenarios to a new JSON file
with open("./filtered_scenarios.json", 'w') as file:
    json.dump(filtered_scenarios, file, indent=4)
print(f"Filtered scenarios saved to: ./filtered_scenarios.json")

with open("./filtered_scenarios.json", 'r') as file:
    scenarios = json.load(file)

# Individual generation
toolbox.register("attr_bool", np.random.choice, len(scenarios), replace=False, size=100)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.attr_bool)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evaluate(individual):
    selected_scenarios = [scenarios[i] for i in individual]
    probability = np.mean([calculate_collision_probability(s) for s in selected_scenarios])
    diversity = calculate_diversity(selected_scenarios)
    intensity = np.mean([s["Intensity"] for s in selected_scenarios])
    return probability, diversity, intensity

toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)
toolbox.register("select", tools.selNSGA2)

# Number of generations
NGEN = 50
MU = 50
LAMBDA = 100
CXPB = 0.7
MUTPB = 0.2

population = toolbox.population(n=MU)
algorithms.eaMuPlusLambda(population, toolbox, mu=MU, lambda_=LAMBDA, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN, stats=None)
fronts = tools.sortNondominated(population, len(population), first_front_only=False)

unique_scenarios_idx = set()  # To keep track of unique scenario identifiers
selected_scenarios = []  # To store the actual selected scenarios

reached_target = False  # Flag to indicate when we've reached 100 unique scenarios

# User choice (could be input from command line or a GUI)
user_choice = input("Enter your choice (vehicle/pedestrian): ")  # Other option could be "vehicle"

# Filter function based on user choice
filter_function = is_pedestrian_or_cyclist_collision if user_choice == "pedestrian" else is_vehicle_collision

# Modified loop to consider only scenarios of a specific collision type
for front in fronts:
    for ind in front:
        if reached_target:
            break
        
        ind_scenarios = [scenarios[i] for i in ind if filter_function(scenarios[i])]  # Apply filter here
        
        for scenario in ind_scenarios:
            if scenario['Scenario Name'] not in unique_scenarios_idx:
                unique_scenarios_idx.add(scenario['Scenario Name'])
                selected_scenarios.append(scenario)
                
                if len(selected_scenarios) >= 100:
                    reached_target = True
                    break

    if reached_target:
        break

# Save to JSON
output_file_path = "./selected_scenarios.json"
with open(output_file_path, 'w') as outfile:
    json.dump(selected_scenarios, outfile, indent=4)

# Read the selected scenarios from the JSON file
with open(output_file_path, 'r') as infile:
    selected_scenarios = json.load(infile)

# Calculate the metrics for the selected scenarios
# Note: The calculation functions and 'normalize' function are assumed to be defined as before

# Calculate average collision probability
average_probability = np.mean([calculate_collision_probability(scenario) for scenario in selected_scenarios])

# Calculate diversity
diversity = calculate_diversity(selected_scenarios)

# Calculate average intensity
average_intensity = np.mean([scenario["Intensity"] for scenario in selected_scenarios])

# Collect the metrics in a dictionary
metrics = {
    "Average Collision Probability": average_probability,
    "Diversity Index": diversity,
    "Average Intensity": average_intensity
}

# Specify the file path for storing the results
results_file_path = "./nsga2_results.json"

# Save the metrics to the JSON file
save_metrics_to_json(results_file_path, metrics)

print("Metrics saved to:", results_file_path)

# Print the calculated metrics
print(f"Average Collision Probability: {average_probability}")
print(f"Diversity Index: {diversity}")
print(f"Average Intensity: {average_intensity}")

print("Selected scenarios saved to:", output_file_path)
