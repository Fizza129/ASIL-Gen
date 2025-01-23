import json
import numpy as np
import random
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

def get_intensity(scenario):
    intensity = scenario["Intensity"]

    return intensity

def calculate_score(scenario):
    probability = calculate_collision_probability(scenario)
    intensity = scenario["Intensity"]
    # Consider integrating the diversity factor directly into the score if diversity is a key factor
    return probability + intensity

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

# User choice (could be input from command line or a GUI)
user_choice = input("Enter your choice (vehicle/pedestrian): ")  # Other option could be "vehicle"

# Filter function based on user choice
filter_function = is_pedestrian_or_cyclist_collision if user_choice == "pedestrian" else is_vehicle_collision

# Load scenarios
with open("./scenarios.json", 'r') as file:
    all_scenarios = json.load(file)
    scenarios = list(filter(filter_function, all_scenarios))

# Prepare a list to store the results
asil_results = []

for scenario in scenarios:
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

def relaxed_selection(scenarios, selected_scenarios):
    """Fills up the selection to 100 scenarios with a more relaxed approach."""
    remaining_scenarios = [s for s in scenarios if s not in selected_scenarios]
    random.shuffle(remaining_scenarios)  # Randomize the order of consideration

    while len(selected_scenarios) < 100 and remaining_scenarios:
        candidate = remaining_scenarios.pop(0)
        selected_scenarios.append(candidate)
    
    return selected_scenarios

def select_scenarios(scenarios):
    selected_scenarios = []
    remaining_scenarios = scenarios[:]  # Copy to avoid modifying the original list

    while len(selected_scenarios) < 100 and remaining_scenarios:
        candidate = random.choice(remaining_scenarios)
        if not selected_scenarios:  # Directly add the first scenario without comparison
            selected_scenarios.append(candidate)
        else:
            # Calculate scores for comparison and diversity
            temp_selected = selected_scenarios + [candidate]
            temp_diversity = calculate_diversity(temp_selected)
            current_diversity = calculate_diversity(selected_scenarios)
            
            candidate_score = calculate_score(candidate)
            better_than_any = any(calculate_score(s) < candidate_score for s in selected_scenarios)
            
            # Check if the candidate maintains or improves diversity and has a better score than any selected scenario
            if better_than_any and temp_diversity >= current_diversity:
                selected_scenarios.append(candidate)
                
        remaining_scenarios.remove(candidate)  # Remove the candidate from the pool after evaluation
    
    # If the selected scenarios are less than 100, fill up the rest with remaining scenarios
    if len(selected_scenarios) < 100:
        selected_scenarios = relaxed_selection(scenarios, selected_scenarios)
    
    return selected_scenarios

selected_scenarios = select_scenarios(scenarios)
            
# Save the most critical 100 scenarios
output_file_path = "./selected_scenarios.json"
with open(output_file_path, 'w') as outfile:
    json.dump(selected_scenarios, outfile, indent=4)

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
results_file_path = "./random_search_results.json"

# Save the metrics to the JSON file
save_metrics_to_json(results_file_path, metrics)

print("Metrics saved to:", results_file_path)

# Print the calculated metrics
print(f"Average Collision Probability: {average_probability}")
print(f"Diversity Index: {diversity}")
print(f"Average Intensity: {average_intensity}")

