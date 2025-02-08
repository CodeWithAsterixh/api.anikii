from fastapi import APIRouter # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix


router = APIRouter()

@router.get("/listTmp")
async def listTmp():
    clearedRouteTemps = get_files_with_prefix()
    
    return {
        "message": "all files in temp directory",
        "files": clearedRouteTemps
    }, 200
