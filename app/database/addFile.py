from .collection import collection_name
from typing import Any, Dict, List


def addToDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Insert a new document with name and data fields."""
    collection_name.insert_one({"name": fileName, "data": data})


def updateInDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Update the document by name using a MongoDB update document (supports operators like $set)."""
    collection_name.update_one(
        {"name": fileName},
        data,
        upsert=True,
    )


def findFileByName(name: str):
    """Find a single document by name."""
    return collection_name.find_one({"name": name})


    