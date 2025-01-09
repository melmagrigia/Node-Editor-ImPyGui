import json
import re
import requests

def perform_post_request(payload, url):
    """
    Perform a POST request with the specified payload and URL.

    Args:
        payload (dict): The data to send in the POST request.
        url (str): The target URL for the POST request.

    Returns:
        Response: The response object from the POST request.
    """
    # Define the headers
    headers = {"Content-Type": "application/json"}

    try:
        # Send the POST request
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        return response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def perform_get_request(url):
    """
    Perform a GET request to the specified URL.

    Args:
        url (str): The target URL for the GET request.

    Returns:
        Response: The response object from the GET request.
    """
    try:
        # Send the GET request
        response = requests.get(url)
        return response

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def get_operation_ids(json_file):
    try:
        # Read the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Check if the "short" key exists in the JSON structure
        if "short" not in data:
            print("Key 'short' not found in the JSON file.")
            return []

        # Extract the list of objects under the "short" key
        short_list = data["short"]

        # Extract the "operation id" from each object in the list
        operation_ids = [obj["operation id"] for obj in short_list if "operation id" in obj]

        return operation_ids

    except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
        print(f"An error occurred: {e}")
        return []


def get_distinct_non_logical_substrings(json_file):
    # Define the set of excluded terms (logical operators and boolean values) as lowercase for case-insensitive matching
    excluded_terms = {"and", "or", "not", "true", "false"}

    # Initialize a set to store unique substrings
    unique_substrings = set()

    try:
        # Read the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Iterate over the objects under the "short" key
        if "short" in data:
            for obj in data["short"]:
                # Extract Preconditions and Effects if they exist
                preconditions = obj.get("Preconditions", "")
                effects = obj.get("Effects", "")

                # Combine both strings for processing
                combined_text = f"{preconditions} {effects}"

                # Use regex to find all alphanumeric substrings (words)
                substrings = re.findall(r'\b[a-zA-Z_]+\b', combined_text)

                # Add valid substrings to the set (excluding logical operators and booleans)
                for substring in substrings:
                    if substring.lower() not in excluded_terms:  # Case-insensitive exclusion
                        unique_substrings.add(substring)

        return list(unique_substrings)

    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"An error occurred: {e}")
        return []