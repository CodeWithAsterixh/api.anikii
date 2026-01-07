from app.core.logger import logger
from .collection import get_collection
from typing import Any, Dict, List


async def addToDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Insert a new document with name and data fields."""
    try:
        collection = get_collection()
        await collection.insert_one({"name": fileName, "data": data})
        logger.info(f"Added {fileName} to database")
    except Exception as e:
        logger.error(f"Failed to add {fileName} to database: {e}")


async def updateInDb(fileName: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
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

    collection = get_collection()
    await collection.update_one(
        {"name": fileName},
        update_doc,
        upsert=True,
    )
    logger.info(f"Updated {fileName} in database")


async def findFileByName(name: str):
    """Find a single document by name."""
    collection = get_collection()
    return await collection.find_one({"name": name})


    