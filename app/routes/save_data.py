from fastapi import APIRouter # type: ignore
from pydantic import BaseModel # type: ignore
from app.database.addFile import findFileByName,addToDb

router = APIRouter()

# Data model for request body
class Item(BaseModel):
    name: str
    data: dict | list
    

# Route to handle POST request
@router.post("/savefile")
async def savefile(item: Item):
    
    saved = findFileByName(item.name)
    if saved:
        return {"message": "File already exists", "data": saved}
    
    addToDb(item.name, item.data)
    
    
    return {"message": "Item added successfully", "data": {
        "name":item.name,
        "content":item.data
        }, }
