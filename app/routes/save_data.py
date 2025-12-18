from fastapi import APIRouter, Request # type: ignore
from pydantic import BaseModel # type: ignore
from app.database.addFile import findFileByName, addToDb
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()

# Data model for request body
class Item(BaseModel):
    name: str
    data: dict | list
    

# Route to handle POST request
@router.post("/savefile")
async def savefile(request: Request, item: Item):
    try:
        saved = findFileByName(item.name)
        if saved:
            data = {"message": "File already exists", "data": saved}
            meta = {"save": {"exists": True, "name": item.name}}
            return success_response(request, data=data, meta=meta)
        addToDb(item.name, item.data)
        data = {
            "message": "Item added successfully",
            "data": {
                "name": item.name,
                "content": item.data
            }
        }
        meta = {"save": {"exists": False, "name": item.name}}
        return success_response(request, data=data, meta=meta)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to save item", error=str(e))
