from fastapi import APIRouter, Request # type: ignore
from app.helpers.json.getTmpLs import  get_files_with_prefix
from app.helpers.json.clearTmp import delete_specific_file
from app.helpers.response_envelope import success_response, error_response


router = APIRouter(prefix="/clearTmp", tags=["name"])


@router.get("/{name}")
async def clearTmpSpecific(request: Request, name:str):
    available_files = get_files_with_prefix()
    formatted_name = name
    if ".json" not in formatted_name:
        formatted_name = f"{name}.json"
    
    if formatted_name in available_files:
        delete_specific_file(formatted_name)
        data = {
            "message": f"{formatted_name} has been deleted",
            "files": formatted_name
        }
        return success_response(request, data=data)
    else:
        print("is not available")
        
    data = {
        "message": f"{formatted_name} is not available",
        "files": formatted_name
    }
    # Not found case but original returned 200; we keep 200 for compatibility
    return success_response(request, data=data)


