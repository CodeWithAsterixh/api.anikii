from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.clearTmp import delete_specific_file
from app.helpers.json.jsonParser import jsonLoad,jsonLoadMeta
from app.helpers.json.jsonFormatRaw import generate_metadata
from app.database.addFile import findFileByName
from app.database.deleteFile import DeleteDb
from app.database.collection import collection_name



router = APIRouter(prefix="/listTmp", tags=["name"])


@router.get("/{name}")
async def getTmpSpecific(name:str, storage:str="local"):
    available_files = get_files_with_prefix()
    formatted_name = name
    data = {}
    meta = {}
    pages_length = 0
    total_items = 0
    thumbnail = None
    gotten_from = storage
           
    if ".json" in formatted_name:
        formatted_name = name.replace(".json", "")
        
    foundDbData = findFileByName(f"{formatted_name}.json")
    if storage == "db" and foundDbData:
        data = foundDbData.get("data",{})
        meta = {
            **generate_metadata(data),
            "name": f"{formatted_name}.json",
            "type": "json"
        }
        
        
        
    
    elif storage == "local" and f"{formatted_name}.json" in available_files:
        data = jsonLoad(formatted_name)
        meta = jsonLoadMeta(formatted_name)
        
    if isinstance(data, list):
        total_items = len(data)
        if total_items > 0 and not isinstance(data[0], str):
            thumbnail = data[0].get("coverImage",{}).get("cover_image",None)
    
    if not isinstance(data, list) and data.get("pages"):
        pages_length = len(data["pages"])
        # Step 1: Get all pages and sort them numerically
        sorted_page_keys = sorted(data["pages"].keys(), key=int)  # Ensure sorting is numerical

        # Step 2: Get the first page (if available)
        first_page_key = sorted_page_keys[0] if sorted_page_keys else None
        first_page_items = data["pages"].get(first_page_key, []) if first_page_key else []

        # Step 3: Get the first item from that first page
        first_item = first_page_items[0] if first_page_items else None
        # Step 4: Calculate total number of items in all pages
        total_items = sum(len(items) for items in data["pages"].values())
        thumbnail = first_item.get("coverImage",{}).get("cover_image",None)
    if not isinstance(data, list) and not data.get("pages"):
        thumbnail = data.get("coverImage",{}).get("cover_image",None)

    result = {
    "message": f"{formatted_name} is available",
    "meta":{
        **meta,
        "pages": pages_length,
        "total":total_items,
        "thumbnail": thumbnail,
        "from": gotten_from
    },
    "data": data,
    }
    
    if data:
        return result, 200
    
    
    
    return {
        "message": f"{formatted_name} is not available in {storage} storage",
        "data": {}
    }, 404



@router.delete("/{name}")
async def clearTmpSpecific(name:str, storage:str="local"):
    formatted_name = name
    deleted = False
    if ".json" not in formatted_name:
        formatted_name = f"{formatted_name}.json"
        
    if storage == "local":
        deleted = delete_specific_file(formatted_name)
        
    elif storage == "db":
        deleted = DeleteDb(formatted_name)
                
    if deleted:
        return{
            "message": f"{formatted_name} has been deleted from {storage} storage",
            "data": {}
        }, 200
    
    return {
        "message": f"{formatted_name} is not available in {storage} storage",
        "data": {}
    }, 404


