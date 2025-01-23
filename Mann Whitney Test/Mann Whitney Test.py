import json
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt

# Function to read metrics from a JSON file
def read_metrics_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def perform_statistical_test_and_print_results(metric_name, data1, data2):
    # Perform the Mann-Whitney U test
    u_statistic, p_value = stats.mannwhitneyu(data1, data2, alternative='two-sided')
    print(f"{metric_name} - U Statistic: {u_statistic}, p-value: {p_value}")

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

def plot_comparison(metric_name, data1, data2, labels):
    data = [data1, data2]
    plt.figure(figsize=(10, 6))
    plt.boxplot(data, labels=labels)
    plt.title(f'Comparison of {metric_name}')
    plt.ylabel(metric_name)
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()

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

# Perform and print statistical tests and comparisons
perform_statistical_test_and_print_results('Average Collision Probability', nsga2_collision_probabilities, random_search_collision_probabilities)
perform_statistical_test_and_print_results('Diversity Index', nsga2_diversities, random_search_diversities)
perform_statistical_test_and_print_results('Average Intensity', nsga2_intensities, random_search_intensities)

# Plotting comparison for each metric
plot_comparison('Average Collision Probability', nsga2_collision_probabilities, random_search_collision_probabilities, ['NSGA-II', 'Random Search'])
plot_comparison('Diversity Index', nsga2_diversities, random_search_diversities, ['NSGA-II', 'Random Search'])
plot_comparison('Average Intensity', nsga2_intensities, random_search_intensities, ['NSGA-II', 'Random Search'])
