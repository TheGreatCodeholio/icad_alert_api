import json

import requests
from json import JSONDecodeError

# Configuration variables for the user to set
JSON_FILE_PATH = '/home/ian/PycharmProjects/icad_alert_api/test_json/gvems.json'

ALERT_CONFIG = {
    "api_url": "http://localhost:8002/process_alert",
    "api_key": "1234-1234-1234-1234"
}


def load_call_data(json_file_path):
    """
    Loads the configuration file and encryption key.
    """

    # Attempt to load the configuration file
    try:
        with open(json_file_path, 'r') as f:
            call_data = json.load(f)
        return call_data
    except FileNotFoundError:
        print(f'JSON file {json_file_path} not found.')
    except json.JSONDecodeError:
        print(f'JSON file {json_file_path} is not in valid JSON format.')
        return None
    except Exception as e:
        print(f'Unexpected Exception Loading JSON file {json_file_path} - {e}')
        return None


def upload_to_icad_alert(alert_config, call_data):
    url = alert_config.get('api_url', "")
    api_key = alert_config.get("api_key", "")
    print(f'Uploading To iCAD Alerting: {url}')

    # Build Headers with API Auth Key
    api_headers = {
        "Authorization": api_key
    }

    try:
        response = requests.post(url, headers=api_headers, json=call_data)

        response.raise_for_status()
        print(
            f"Successfully uploaded to iCAD Alerting: {url}")
        return True
    except requests.exceptions.RequestException as e:
        # This captures HTTP errors, connection errors, etc.
        print(
            f'Failed Uploading To iCAD Alerting: {e.response.status_code} - {e.response.json().get("message", "No detailed message provided")}')
    except Exception as e:
        # Catch-all for any other unexpected errors
        print(f'An unexpected error occurred while upload to iCAD Alerting {url}: {e}')

    return False


# Get Call Metadata from File
call_data = load_call_data(JSON_FILE_PATH)
if call_data:
    # Example usage of the function with configurable file paths and URL
    upload_to_icad_alert(ALERT_CONFIG, call_data)
