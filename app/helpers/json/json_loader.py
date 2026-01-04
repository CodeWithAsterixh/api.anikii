import os
import json
import tempfile
from app.helpers.security import validate_safe_path

# Use a cross-platform temp directory
BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")

def jsonLoad(fileName: str) -> dict:
    """
    Loads data from a JSON file if it exists; otherwise, returns an empty dictionary.
    """
    json_path = validate_safe_path(f"{fileName}.json")
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
    """
    import time
    json_path = validate_safe_path(f"{fileName}.json")
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
