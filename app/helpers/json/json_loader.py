import os
import json
import tempfile
import time
import aiofiles
from typing import Optional
from app.helpers.security import validate_safe_path

from app.core.logger import logger

# Use a cross-platform temp directory
BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")

async def jsonLoad(fileName: str, ttl: Optional[int] = None) -> dict:
    """
    Loads data from a JSON file if it exists and is not expired; otherwise, returns an empty dictionary.
    
    Args:
        fileName: Name of the file to load (without extension)
        ttl: Optional time-to-live in seconds. If provided, file will be ignored if older than TTL.
    """
    json_path = validate_safe_path(f"{fileName}.json")
    logger.debug(f"Loading data from {json_path}")

    if os.path.exists(json_path):
        if ttl is not None:
            mtime = os.path.getmtime(json_path)
            if time.time() - mtime > ttl:
                logger.info(f"Cache expired for {fileName} (mtime: {time.ctime(mtime)}, TTL: {ttl}s)")
                return {}
        try:
            async with aiofiles.open(json_path, mode="r", encoding="utf-8-sig") as file:
                content = await file.read()
                return json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            logger.error(f"JSON file {json_path} is corrupted or has invalid encoding. Returning empty data.")
            return {}
    return {}

async def jsonLoadMeta(fileName: str) -> dict:
    """
    Loads meta data from a JSON file if it exists; otherwise, returns an empty dictionary.
    """
    import time
    json_path = validate_safe_path(f"{fileName}.json")
    logger.debug(f"Loading metadata from {json_path}")

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
        except Exception as e:
            logger.error(f"Error reading metadata for {json_path}: {e}")
            return {}
    return {}
