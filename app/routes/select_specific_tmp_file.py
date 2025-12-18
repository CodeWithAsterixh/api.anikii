from fastapi import APIRouter, HTTPException, Request # type: ignore
from app.helpers.json.getTmpLs import get_files_with_prefix
from app.database.collection import collection_name
from app.helpers.json.jsonParser import jsonWrite
from app.helpers.response_envelope import success_response, error_response

router = APIRouter(prefix="/save", tags=["Name"])


@router.get("/{name}")
async def saveSpecific(request: Request, name:str):
    files = get_files_with_prefix()
    formattedName = name
    if ".json" not in formattedName:
        formattedName = f"{name}.json"
    
    if formattedName in files:
        # If exists on local, also ensure it exists in DB
        nameDB = formattedName.replace(".json", "")
        isExistedInDb = list(collection_name.find({"name": nameDB}))
        if len(isExistedInDb) <= 0:
            jsonWrite(formattedName, True)
        data = {
            "message": "File already exists or is saved",
            "files": formattedName
        }
        return success_response(request, data=data)
    
    try:
        jsonWrite(formattedName, True)
        data = {
            "message": "file saved",
            "files": formattedName
        }
        return success_response(request, data=data)
    except Exception as e:
        return error_response(request, status_code=500, message="save failed", error=str(e))


