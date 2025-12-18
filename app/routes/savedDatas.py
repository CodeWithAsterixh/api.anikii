from fastapi import APIRouter, HTTPException, Query, Request  # type: ignore
from app.helpers.json.getTmpLs import get_files_with_prefix
from app.helpers.json.clearTmp import clear_anikii_route
from app.database.collection import collection_name
from typing import List, Dict, Any
from app.helpers.response_envelope import success_response, error_response

router = APIRouter()


@router.get("/saved")
async def list_saved_data(request: Request) -> Dict[str, Any]:
    """List saved data from local temp storage and MongoDB."""
    temps: List[str] = get_files_with_prefix()
    # Use PyMongo find with projection to get names efficiently
    db_items: List[str] = [
        doc.get("name")
        for doc in collection_name.find({}, {"name": 1, "_id": 0})
        if doc.get("name")
    ]

    data = {
        "message": "all files in temp directory",
        "files": {
            "local": temps,
            "db": db_items,
        },
    }
    meta = {"saved": {"local_count": len(temps), "db_count": len(db_items)}}
    return success_response(request, data=data, meta=meta)


@router.delete("/saved")
async def clear_saved_data(
    request: Request,
    storage: str = Query(
        default="local",
        description="Storage to clear: 'local' or 'db'",
        regex=r"^(local|db)$",
    )
) -> Dict[str, Any]:
    """Clear saved data from the specified storage (local or db)."""
    temps: List[str] = get_files_with_prefix()
    db_items: List[str] = [
        doc.get("name")
        for doc in collection_name.find({}, {"name": 1, "_id": 0})
        if doc.get("name")
    ]

    if storage == "local":
        if len(temps) > 0:
            clear_anikii_route()
            data = {"message": f"{storage} storage cleared", "files": temps}
            meta = {"saved": {"storage": storage, "cleared_count": len(temps)}}
            return success_response(request, data=data, meta=meta)
        data = {"message": f"{storage} storage is empty", "files": {}}
        meta = {"saved": {"storage": storage, "cleared_count": 0}}
        return success_response(request, data=data, meta=meta)

    if storage == "db":
        if len(db_items) > 0:
            collection_name.delete_many({})
            data = {"message": f"{storage} storage cleared", "files": db_items}
            meta = {"saved": {"storage": storage, "cleared_count": len(db_items)}}
            return success_response(request, data=data, meta=meta)
        data = {"message": f"{storage} storage is empty", "files": {}}
        meta = {"saved": {"storage": storage, "cleared_count": 0}}
        return success_response(request, data=data, meta=meta)

    # Should be unreachable due to Query regex; keep for safety
    return error_response(request, status_code=400, message=f"{storage} storage is not available", error={"storage": storage})
