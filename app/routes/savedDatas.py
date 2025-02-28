from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.clearTmp import clear_anikii_route
from app.database.collection import collection_name

router = APIRouter()

@router.get("/saved")
async def listSavedData():
    Temps = get_files_with_prefix()
    
    items = collection_name.find().to_list()
    
    dbItems  = []
    
    for name in items:
        if name.get("name"):
            dbItems.append(name.get("name"))
    
    return {
        "message": "all files in temp directory",
        "files": {
            "local":Temps,
            "db":dbItems
        },
    }, 200


@router.delete("/saved")
async def listSavedData(storage="local"):
    # get data first
    Temps = get_files_with_prefix()
    
    items = collection_name.find().to_list()
    
    dbItems  = []
    
    for name in items:
        if name.get("name"):
            dbItems.append(name.get("name"))
    
    if storage == "local" and len(Temps)>0:
        clear_anikii_route()
        return {
            "message": f"{storage} storage cleared",
            "files": Temps
        }, 200
    elif storage == "db" and len(dbItems)>0:
        collection_name.delete_many({})
        return {
            "message": f"{storage} storage cleared",
            "files": dbItems
        }, 200
    
    if storage == "local" or storage =="db":
        return {
            "message": f"{storage} storage is empty",
            "files": {},
        }, 200
    return {
        "message": f"{storage} storage is not available",
        "files": {},
    }, 200
