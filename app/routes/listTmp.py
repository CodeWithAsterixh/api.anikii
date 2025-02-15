from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.database.collection import collection_name

router = APIRouter()

@router.get("/listTmp")
async def listTmp():
    clearedRouteTemps = get_files_with_prefix()
    
    items = collection_name.find().to_list()
    
    itemsName  = []
    
    for name in items:
        if name.get("name"):
            itemsName.append(name.get("name"))
    
    return {
        "message": "all files in temp directory",
        "files": list(set(clearedRouteTemps) | set(itemsName)),
    }, 200
