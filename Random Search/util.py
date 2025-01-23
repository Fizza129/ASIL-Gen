import os
import json

def save_metrics_to_json(file_path, metrics):
    if os.path.exists(file_path):
        with open(file_path, 'r+') as file:
            # Read current data
            data = json.load(file)
            # Append new metrics
            data.append(metrics)
            # Move the cursor to the beginning of the file
            file.seek(0)
            # Update the file with new data
            json.dump(data, file, indent=4)
    else:
        with open(file_path, 'w') as file:
            # Create a new file with the metrics
            json.dump([metrics], file, indent=4)
