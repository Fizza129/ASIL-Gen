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

# Define the problem object
creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0, 1.0)) # Maximize probability and intensity, minimize (maximize negative) diversity
creator.create("Individual", list, fitness=creator.FitnessMulti)

toolbox = base.Toolbox()

# Assume scenarios is your list of scenarios loaded from JSON
with open("./scenarios.json", 'r') as file:
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
