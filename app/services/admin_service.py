import os
import logging
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
from app.core.constants import NAME_END_JSON
from app.helpers.json.getTmpLs import get_files_with_prefix
from app.helpers.json.clearTmp import delete_specific_file, clear_anikii_route
from app.helpers.json.json_writer import json_write
from app.database.collection import get_collection
from app.database.addFile import find_file_by_name, add_to_db
from app.helpers.security import validate_safe_path

logger = logging.getLogger(__name__)

def list_tmp_files() -> List[str]:
    """List all files in the temp directory."""
    return get_files_with_prefix()

def delete_tmp_file(name: str):
    """Delete a specific temp file."""
    # Ensure it's a .json file for safety if that's the convention
    if not name.endswith(NAME_END_JSON):
        name = f"{name}.json"
    
    # validate_safe_path will raise HTTPException if unsafe
    
    available_files = get_files_with_prefix()
    if name in available_files:
        delete_specific_file(name)
        return True
    return False

async def save_tmp_to_db(name: str):
    """Save a temp file reference to the database."""
    if not name.endswith(NAME_END_JSON):
        name = f"{name}.json"
    
    validate_safe_path(name)
    
    available_files = get_files_with_prefix()
    if name in available_files:
        name_db = name.replace(NAME_END_JSON, "")
        collection = get_collection()
        is_existed = await collection.find_one({"name": name_db})
        if not is_existed:
            json_write(name, True)
        return True
    
    # If file doesn't exist locally, we can still try to "save" it via json_write 
    # (which seems to be the original behavior in select_specific_tmp_file.py)
    try:
        json_write(name, True)
        return True
    except Exception as e:
        logger.error(f"Error in save_tmp_to_db: {e}")
        return False

def save_data_to_db(name: str, data: Any):
    """Save arbitrary data to the database."""
    existing = find_file_by_name(name)
    if existing:
        return {"exists": True, "data": existing}
    
    add_to_db(name, data)
    return {"exists": False, "data": {"name": name, "content": data}}

async def list_db_saved_data() -> List[str]:
    """List all saved data names from the database."""
    collection = get_collection()
    cursor = collection.find({}, {"name": 1, "_id": 0})
    return [
        doc.get("name")
        async for doc in cursor
        if doc.get("name")
    ]

async def clear_storage(storage: str):
    """Clear local temp storage or database storage."""
    if storage == "local":
        files = get_files_with_prefix()
        if files:
            clear_anikii_route()
            return files
        return []
    
    if storage == "db":
        db_items = await list_db_saved_data()
        if db_items:
            collection = get_collection()
            await collection.delete_many({})
            return db_items
        return []
    
    raise ValueError(f"Invalid storage type: {storage}")
