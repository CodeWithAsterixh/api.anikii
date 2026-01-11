from app.core.logger import logger
from .collection import get_collection
from typing import Any, Dict, List


async def add_to_db(file_name: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
    """Insert a new document with name and data fields."""
    try:
        collection = get_collection()
        await collection.insert_one({"name": file_name, "data": data})
        logger.info(f"Added {file_name} to database")
    except Exception as e:
        logger.error(f"Failed to add {file_name} to database: {e}")


async def update_in_db(file_name: str, data: Dict[str, Any] | List[Dict[str, Any]]) -> None:
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
        {"name": file_name},
        update_doc,
        upsert=True,
    )
    logger.info(f"Updated {file_name} in database")


async def find_file_by_name(name: str):
    """Find a single document by name."""
    collection = get_collection()
    return await collection.find_one({"name": name})


    