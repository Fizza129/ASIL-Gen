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

# User choice (could be input from command line or a GUI)
user_choice = input("Enter your choice (vehicle/pedestrian): ")  # Other option could be "vehicle"

# Filter function based on user choice
filter_function = is_pedestrian_or_cyclist_collision if user_choice == "pedestrian" else is_vehicle_collision

# Load scenarios
with open("./scenarios.json", 'r') as file:
    all_scenarios = json.load(file)
    scenarios = list(filter(filter_function, all_scenarios))

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

