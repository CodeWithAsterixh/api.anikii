import os
import json
import tempfile
from app.helpers.security import validate_safe_path
from app.helpers.json.json_loader import jsonLoad

from app.core.logger import logger

# Use a cross-platform temp directory
BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")

def jsonSave(fileName: str, page: int, new_items: dict) -> dict:
    """
    Loads existing JSON data, adds new items to the specified page, and saves the updated data.
    """
    # Ensure the directory exists
    os.makedirs(BASE_TMP_DIR, exist_ok=True)

    json_path = validate_safe_path(f"{fileName}.json")
    logger.debug(f"Saving data to {json_path}")

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
        logger.error(f"Error: 'data' field is missing or not a list in new_items for {fileName}. No changes made.")
        return existing_data

    # Save the updated data
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)
        logger.info(f"Updated cache for {fileName} (page {page})")
        return data
    except Exception as e:
        logger.error(f"Error writing to JSON file {json_path}: {e}")
        return existing_data

def jsonWrite(fileName: str, content):
    """
    Loads existing JSON data, and saves the content to the specified file.
    """
    # Ensure the directory exists
    os.makedirs(BASE_TMP_DIR, exist_ok=True)

    json_path = validate_safe_path(f"{fileName}.json")
    logger.debug(f"Writing content to {json_path}")

    # Save the updated data
    try:
        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(content, file, indent=4)
        logger.info(f"Saved JSON content to {fileName}")
        return content
    except Exception as e:
        logger.error(f"Error writing to JSON file {json_path}: {e}")
        # Return existing data if write fails
        return jsonLoad(fileName)
