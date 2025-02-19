import json
from statistics import median

def calculate_median_duration(json_file_path):
    
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    
    durations = [result['duration'] for result in data['detailed_results']]
    
    
    return median(durations)

if __name__ == "__main__":
    
    file_path = "../onpremises/rsa_onpremises_encrypt.json"
    
    try:
        median_duration = calculate_median_duration(file_path)
        print(f"Median duration: {median_duration:.2f} seconds")
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format")
    except KeyError:
        print("Error: JSON file doesn't contain the expected structure")