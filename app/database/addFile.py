from .collection import collection_name
from typing import Any, Dict, List


def addToDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Insert a new document with name and data fields."""
    collection_name.insert_one({"name": fileName, "data": data})


def updateInDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """
    Update the document by name.
    If 'data' contains MongoDB operators (keys starting with $), it uses them directly.
    Otherwise, it wraps the data in a $set operator for safety.
    """
    # If the first key starts with $, assume it's a valid update document
    if isinstance(data, dict) and data and any(k.startswith('$') for k in data.keys()):
        update_doc = data
    else:
        update_doc = {"$set": {"data": data}}

    collection_name.update_one(
        {"name": fileName},
        update_doc,
        upsert=True,
    )


def findFileByName(name: str):
    """Find a single document by name."""
    return collection_name.find_one({"name": name})


    