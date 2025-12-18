import os
import json
import time
import tempfile

# Use a cross-platform temp directory (e.g., C:\Users\\<User>\\AppData\\Local\\Temp on Windows, /tmp on Linux)
BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")


def jsonLoad(fileName: str) -> dict:
    """
    Loads data from a JSON file if it exists; otherwise, returns an empty dictionary.

    Args:
        fileName (str): The name of the JSON file (without extension).

    Returns:
        dict: The data from the JSON file or an empty dictionary if the file doesn't exist.
    """
    json_path = os.path.join(BASE_TMP_DIR, f"{fileName}.json")
    print(f"Loading data from {json_path}")

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8-sig") as file:
                return json.load(file)
        except (json.JSONDecodeError, UnicodeDecodeError):
            print("Error: JSON file is corrupted or has invalid encoding. Returning empty data.")
            return {}
    return {}


def jsonLoadMeta(fileName: str) -> dict:
    """
    Loads meta data from a JSON file if it exists; otherwise, returns an empty dictionary.

    Args:
        fileName (str): The name of the JSON file (without extension).

    Returns:
        dict: The data from the JSON file or an empty dictionary if the file doesn't exist.
    """
    json_path = os.path.join(BASE_TMP_DIR, f"{fileName}.json")
    print(f"Loading data from {json_path}")

    if os.path.exists(json_path):
        try:
            file_size = os.path.getsize(json_path)
            file_size = round(file_size/1024,2)
            # time stamps
            creation_time = os.path.getctime(json_path)
            modification_time = os.path.getmtime(json_path)
            access_time = os.path.getatime(json_path)
            
            # times to readable format
            
            creation_time = time.ctime(creation_time)
            modification_time = time.ctime(modification_time)
            access_time = time.ctime(access_time)
            
            # o
            
            return {
                "file_size":file_size,
                "creation_time":creation_time,
                "modification_time":modification_time,
                "access_time":access_time,
                "name": f"{fileName}.json",
                "type": "json",          
            }
        except json.JSONDecodeError:
            print("Error: JSON file is corrupted. Returning empty data.")
            return {}
    return {}

def jsonSave(fileName: str, page: int, new_items: dict) -> dict:
    """
    Loads existing JSON data, adds new items to the specified page, and saves the updated data.

    Args:
        fileName (str): The name of the JSON file (without extension).
        page (int): The page number to update.
        new_items (dict): A dictionary containing "lastPage" and a list of new items under "data".

    Returns:
        dict: The final data that was saved.
    """

    # Ensure the directory exists
    os.makedirs(BASE_TMP_DIR, exist_ok=True)

    json_path = os.path.join(BASE_TMP_DIR, f"{fileName}.json")
    print(f"Saving data to {json_path}")

    # Load existing data if available
    existing_data = jsonLoad(fileName)

    # Ensure a structured dictionary
    data = {
        "lastPage": new_items.get("lastPage", existing_data.get("lastPage", 1)),
        "pages": existing_data.get("pages", {})
    }

    # Convert page number to string to ensure consistency in JSON keys
    page_key = str(page)

    # Ensure the specified page exists as a list
    data["pages"].setdefault(page_key, [])

    # Append new items to the page's list
    if isinstance(new_items.get("data"), list):
        data["pages"][page_key].extend(new_items["data"])
    else:
        print(f"Error: 'data' field is missing or not a list. No changes made.")
        return existing_data

    # Save the updated data
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        print("up-tmp")
        return data
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return existing_data

def jsonWrite(fileName: str, content):
    """
    Loads existing JSON data, adds new items to the specified page, and saves the updated data.

    Args:
        fileName (str): The name of the JSON file (without extension).
        page (int): The page number to update.
        new_items (dict): A dictionary containing "lastPage" and a list of new items under "data".

    Returns:
        dict: The final data that was saved.
    """

    # Ensure the directory exists
    os.makedirs(BASE_TMP_DIR, exist_ok=True)

    json_path = os.path.join(BASE_TMP_DIR, f"{fileName}.json")
    print("sv-tmp")


    # Load existing data if available
    existing_data = jsonLoad(fileName)

    # Save the updated data
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(content, file, indent=4)
        print("up-tmp")

        return content
    except Exception as e:
        print(f"Error writing to JSON file: {e}")
        return existing_data
