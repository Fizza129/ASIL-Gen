import json
import numpy as np
from scipy import stats

# Function to read metrics from a JSON file
def read_metrics_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def perform_statistical_test_and_calculate_effect_size(metric_name, data1, data2):
    # Perform the Mann-Whitney U test
    u_statistic, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
    print(f"{metric_name} - U Statistic: {u_statistic}, p-value: {p_value}")

    # Calculate the z-value
    n1 = len(data1)
    n2 = len(data2)
    mean_u = n1 * n2 / 2
    std_u = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    z_value = (u_statistic - mean_u) / std_u
    print(f"{metric_name} - z-value: {z_value}")

    # Calculate the effect size (rank-biserial correlation)
    n = n1 + n2
    effect_size = z_value / np.sqrt(n)
    print(f"{metric_name} - Effect Size (r): {effect_size}")

    # Interpret the results
    if p_value < 0.05:
        print(f"There is a statistically significant difference in '{metric_name}' between the two groups.")
    else:
        print(f"There is no statistically significant difference in '{metric_name}' between the two groups.")

    # Calculate and print median values
    median1 = np.median(data1)
    median2 = np.median(data2)
    print(f"NSGA-II Median {metric_name}: {median1}")
    print(f"Random Search Median {metric_name}: {median2}")

    # Determine which algorithm performed better
    if median1 > median2:
        print(f"NSGA-II has performed better in terms of '{metric_name}'.\n")
    else:
        print(f"Random Search has performed better in terms of '{metric_name}'.\n")

# Load results from JSON files
nsga2_results = read_metrics_from_json("nsga2_results.json")
random_search_results = read_metrics_from_json("random_search_results.json")

# Extract metrics
nsga2_collision_probabilities = [result["Average Collision Probability"] for result in nsga2_results]
random_search_collision_probabilities = [result["Average Collision Probability"] for result in random_search_results]

nsga2_diversities = [result["Diversity Index"] for result in nsga2_results]
random_search_diversities = [result["Diversity Index"] for result in random_search_results]

nsga2_intensities = [result["Average Intensity"] for result in nsga2_results]
random_search_intensities = [result["Average Intensity"] for result in random_search_results]

# Perform and print statistical tests and effect sizes
perform_statistical_test_and_calculate_effect_size('Average Collision Probability', nsga2_collision_probabilities, random_search_collision_probabilities)
perform_statistical_test_and_calculate_effect_size('Diversity Index', nsga2_diversities, random_search_diversities)
perform_statistical_test_and_calculate_effect_size('Average Intensity', nsga2_intensities, random_search_intensities)
