from fastapi import APIRouter # type: ignore
from pydantic import BaseModel # type: ignore
from app.database.addFile import findFileByName,addToDb
from app.database.deleteFile import DeleteDb


router = APIRouter()

# Data model for request body
class Item(BaseModel):
    name: str

# Route to handle POST request
@router.post("/delete")
async def savefile(item: Item):
    
    saved = findFileByName(item.name)
    if saved:
        DeleteDb(item.name)
        return {"message": "File deleted successfully", "data": {}}
    
    return {"message": "Item not found", "data": {}, }
