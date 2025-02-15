from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.jsonParser import jsonLoad,jsonLoadMeta
from app.helpers.json.jsonFormatRaw import generate_metadata
from app.database.addFile import findFileByName



router = APIRouter(prefix="/listTmp", tags=["name"])


@router.get("/{name}")
async def clearTmpSpecific(name:str):
    available_files = get_files_with_prefix()
    formatted_name = name
    data = {}
    meta = {}
    pages_length = 0
    total_items = 0
    thumbnail = None
    gotten_from = "temp"
           
    if ".json" in formatted_name:
        formatted_name = name.replace(".json", "")
        
        
    foundDbData = findFileByName(f"{formatted_name}.json")
    if foundDbData:
        data = foundDbData.get("data",{})
        meta = {
            **generate_metadata(data),
            "name": f"{formatted_name}.json",
            "type": "json"
        }
        gotten_from = "db"
        
        
        
    
    elif f"{formatted_name}.json" in available_files:
        data = jsonLoad(formatted_name)
        meta = jsonLoadMeta(formatted_name)
        gotten_from = "temp"
        
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
        "message": f"{formatted_name} is not available",
        "data": {}
    }, 200


