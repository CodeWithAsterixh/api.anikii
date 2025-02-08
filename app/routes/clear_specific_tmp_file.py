from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.clearTmp import delete_specific_file



router = APIRouter(prefix="/clearTmp", tags=["name"])


@router.get("/{name}")
async def clearTmpSpecific(name:str):
    available_files = get_files_with_prefix()
    formatted_name = name
    if ".json" not in formatted_name:
        formatted_name = f"{name}.json"
    
    if formatted_name in available_files:
        delete_specific_file(formatted_name)
        return {
        "message": f"{formatted_name} has been deleted",
        "files": formatted_name
    }, 200
    else:
        print("is not available")
        
    
    return {
        "message": f"{formatted_name} is not available",
        "files": formatted_name
    }, 200


