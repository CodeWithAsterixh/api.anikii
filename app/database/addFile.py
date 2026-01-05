from app.core.logger import logger
from .collection import collection_name
from typing import Any, Dict, List


def addToDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Insert a new document with name and data fields."""
    try:
        collection_name.insert_one({"name": fileName, "data": data})
        logger.info(f"Added {fileName} to database")
    except Exception as e:
        logger.error(f"Failed to add {fileName} to database: {e}")


def updateInDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """
    Update the document by name.
    Strictly enforces the use of the $set operator to prevent NoSQL injection of other operators.
    """
    # Always wrap in $set unless it's already a safe update document
    # For security, we only allow $set if it's explicitly provided as a top-level operator
    if isinstance(data, dict) and len(data) == 1 and "$set" in data:
        update_doc = data
    else:
        update_doc = {"$set": {"data": data}}

    collection_name.update_one(
        {"name": fileName},
        update_doc,
        upsert=True,
    )
    logger.info(f"Updated {fileName} in database")


def findFileByName(name: str):
    """Find a single document by name."""
    return collection_name.find_one({"name": name})


    