from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.jsonParser import jsonLoad,jsonLoadMeta



router = APIRouter(prefix="/listTmp", tags=["name"])


@router.get("/{name}")
async def clearTmpSpecific(name:str):
    available_files = get_files_with_prefix()
    formatted_name = name
    if ".json" in formatted_name:
        formatted_name = name.replace(".json", "")
    
    if f"{formatted_name}.json" in available_files:
        data = jsonLoad(formatted_name)
        meta = jsonLoadMeta(formatted_name)
        return {
        "message": f"{formatted_name} is available",
        "meta":meta,
        "data": data,
    }, 200
    else:
        print("is not available")
        
    
    return {
        "message": f"{formatted_name} is not available",
        "data": {}
    }, 200


