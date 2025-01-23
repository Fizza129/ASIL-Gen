import random
import re
import xml.etree.ElementTree as ET


def random_integer(min_val, max_val):
    return random.randint(min_val, max_val)

# Function to generate a random floating-point value within a range with specified precision
def random_float(min_val, max_val, precision):
    return round(random.uniform(min_val, max_val), precision)

# Function to modify the variables in the Python file
def modify_variables(original_code, original_xml, variable_ranges, num_variations):
    print("Modifying variables...")
    modified_data = []
    for i in range(num_variations):  # Change this line
        print(f"Processing variation {i + 1}...")
        modified_code = original_code
        modified_xml = original_xml

        for variable, value_spec in variable_ranges.items():
            if value_spec is not None:
                if "-" in value_spec:  # Range values
                    if variable == "self.throttle":
                        min_val, max_val = map(float, value_spec.split("-"))
                        modified_value = random_float(min_val, max_val, 2)  # Generate float with 2 decimal places
                    else:
                        min_val, max_val = map(int, value_spec.split("-"))
                        modified_value = random_integer(min_val, max_val)

                elif "/" in value_spec:  # Specific values
                    options = value_spec.split("/")
                    modified_value = random.choice(options)
                else:  # Other specific instructions
                    modified_value = value_spec

                if variable == "weather":
                    options = ["carla.WeatherParameters.ClearNoon", "carla.WeatherParameters.HardRainNoon",
                               "carla.WeatherParameters.ClearNight", "carla.WeatherParameters.HardRainNight"]
                    modified_value = random.choice(options)
                    weather_part = modified_value.split('.')[-1]
                    modified_code = re.sub(r"self\.output\['Weather'\]\s*=\s*\".*\"",
                                           f"self.output['Weather'] = \"{weather_part}\"", modified_code)

                modified_code = re.sub(r'class\s+OppositeVehicleRunningRedLight\s*\(',
                                       f'class OppositeVehicleRunningRedLight_{i + 1}(', modified_code)

                # Update the first occurrence of the class name in the super constructor
                modified_code = re.sub(r'super\(\)\.__init__\("OppositeVehicleJunction"',
                                       rf'super().__init__("OppositeVehicleJunction_{i + 1}"',
                                       modified_code, count=1)

                modified_code = re.sub(rf"\b{re.escape(variable)}\b\s*=\s*[^,\n]*", f"{variable} = {modified_value}",
                                       modified_code)

        modified_code = re.sub(r"self\.output\['Scenario Name'\]\s*=\s*\"OppositeVehicleRunningRedLight\"",
                               f"self.output['Scenario Name'] = \"OppositeVehicleRunningRedLight_{i + 1}\"", modified_code)

        modified_xml = original_xml.replace('type="OppositeVehicleRunningRedLight"',
                                            f'type="OppositeVehicleRunningRedLight_{i + 1}"')

        modified_data.append((modified_code, modified_xml))

    print("Variables modified successfully.")
    return modified_data


# Read the original Python file
with open(r"E:\Games\Carla\scenario_runner-0.9.15\srunner\scenarios\opposite_vehicle_taking_priority.py", "r") as file:
    original_code = file.read()

# Read the original XML file
with open(r"E:\Games\Carla\scenario_runner-0.9.15\srunner\examples\RunningRedLight.xml", "r") as file:
    original_xml = file.read()

# Define the variable ranges you want to change
variable_ranges = {
    "self._adversary_orignal_speed": "15-30",
    "self.throttle": "0.5-1.0",
    "weather": "carla.WeatherParameters.ClearNoon/carla.WeatherParameters.HardRainNoon/carla.WeatherParameters.ClearNight/carla.WeatherParameters.HardRainNight",
}

# Generate multiple variations by modifying variables
num_variations = 1000
print("Generating variations...")
modified_data = modify_variables(original_code, original_xml, variable_ranges, num_variations)
print("Variations generated successfully.")

# Write modified versions to separate files
for i, (modified_code, modified_xml) in enumerate(modified_data):
    print(f"Writing modified files for variation {i + 1}...")
    with open(rf"E:\Games\Carla\scenario_runner-0.9.15\srunner\scenarios\opposite_vehicle_taking_priority_{i + 1}.py",
              "w") as code_file:
        code_file.write(modified_code)

    with open(rf"E:\Games\Carla\scenario_runner-0.9.15\srunner\examples\RunningRedLight_{i + 1}.xml", "w") as xml_file:
        xml_file.write(modified_xml)
    print(f"Modified files for variation {i + 1} written successfully.")