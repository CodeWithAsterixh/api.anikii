from fastapi import APIRouter, Request, Depends, Query, Path
from pydantic import BaseModel, Field
from typing import Any, Dict, List
from app.helpers.response_envelope import success_response, error_response
from app.helpers.security import verify_api_key
from app.services.admin_service import (
    list_tmp_files,
    delete_tmp_file,
    save_tmp_to_db,
    save_data_to_db,
    list_db_saved_data,
    clear_storage
)

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(verify_api_key)])

class SaveFileRequest(BaseModel):
    name: str = Field(..., min_length=1)
    data: Any

@router.get("/tmp")
async def get_all_tmp_files(request: Request):
    """List all temporary files."""
    try:
        files = await list_tmp_files()
        return success_response(request, data={"files": files})
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to list tmp files", error=str(e))

@router.delete("/tmp/{name}")
async def clear_specific_tmp(request: Request, name: str = Path(...)):
    """Delete a specific temporary file."""
    try:
        deleted = await delete_tmp_file(name)
        if deleted:
            return success_response(request, data={"message": f"{name} deleted", "file": name})
        return success_response(request, data={"message": f"{name} not found", "file": name})
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to delete tmp file", error=str(e))

@router.post("/tmp/{name}/save")
async def save_tmp_file_to_db(request: Request, name: str = Path(...)):
    """Save a temporary file's reference to the database."""
    try:
        saved = await save_tmp_to_db(name)
        if saved:
            return success_response(request, data={"message": f"{name} saved to DB", "file": name})
        return error_response(request, status_code=500, message="Failed to save tmp file to DB")
    except Exception as e:
        return error_response(request, status_code=500, message="Error saving tmp file", error=str(e))

@router.get("/db/saved")
async def list_saved_db_data(request: Request):
    """List all saved data in the database and local storage."""
    try:
        local_files = await list_tmp_files()
        db_files = await list_db_saved_data()
        data = {
            "local": local_files,
            "db": db_files
        }
        meta = {"counts": {"local": len(local_files), "db": len(db_files)}}
        return success_response(request, data=data, meta=meta)
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to list saved data", error=str(e))

@router.post("/db/save")
async def save_custom_data(request: Request, body: SaveFileRequest):
    """Save custom data to the database."""
    try:
        result = await save_data_to_db(body.name, body.data)
        if result["exists"]:
            return success_response(request, data={"message": "Data already exists", "data": result["data"]})
        return success_response(request, data={"message": "Data saved successfully", "data": result["data"]})
    except Exception as e:
        return error_response(request, status_code=500, message="Failed to save data", error=str(e))

@router.delete("/storage/clear")
async def clear_all_storage(
    request: Request, 
    storage: str = Query(..., regex="^(local|db)$")
):
    """Clear all data from either local temp storage or the database."""
    try:
        cleared_items = await clear_storage(storage)
        return success_response(request, data={
            "message": f"{storage} storage cleared",
            "cleared_count": len(cleared_items),
            "items": cleared_items
        })
    except Exception as e:
        return error_response(request, status_code=500, message=f"Failed to clear {storage} storage", error=str(e))
