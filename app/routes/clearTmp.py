from fastapi import APIRouter
from app.helpers.json.clearTmp import clear_anikii_route


router = APIRouter()

@router.get("/clearTmp")
async def clearTmp():
    clearedRouteTemps = clear_anikii_route()
    
    return {
        "message": "Cache cleared",
        "files": clearedRouteTemps
    }, 200
