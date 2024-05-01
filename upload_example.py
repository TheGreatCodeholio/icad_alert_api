import json

import requests
from json import JSONDecodeError

# Configuration variables for the user to set
JSON_FILE_PATH = 'test_json/gvems.json'
URL = "http://localhost:8002/process_alert"


def post_json(json_file_path, url):
    """
    Posts an audio file and a JSON file to the specified URL and prints the response.

    Parameters:
    - audio_file_path (str): The file path to the audio file.
    - json_file_path (str): The file path to the JSON file.
    - url (str): The URL to which the files are posted.
    """
    try:
        with open(json_file_path, 'rb') as json_file:
            call_data = json.load(json_file)
            response = requests.post(url, json=call_data)

            try:
                response_data = response.json()
            except JSONDecodeError:
                response_data = response.text

            print(response_data)

    except FileNotFoundError as e:
        print(f"Error: {e}. Please check the file paths.")
    except requests.RequestException as e:
        print(f"Error during the request: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


# Example usage of the function with configurable file paths and URL
post_json(JSON_FILE_PATH, URL)
