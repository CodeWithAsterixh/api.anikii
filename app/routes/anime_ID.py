from fastapi import APIRouter
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.modules import fetch_malsyn_data_and_get_provider

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}")
async def popular(id:int):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("description", "get_descriptions")        
        # Define the variables
        variables = {"id": id}

        # Prepare the body for the API request
        body = {
            "query": query,
            "variables": variables
        }

        # Make the API request
        response = make_api_request(body)  # Assuming make_api_request returns a response object
        data = response["data"]["Media"]
        idSub = await fetch_malsyn_data_and_get_provider(data["id"])

        # Check for errors in the response
        if response.get("errors"):
            return {"error": response["errors"]}, 500

        # Return the parsed result as JSON
        return {"result": {
                    "data": data,
                    "idSub": idSub
                }
            }, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
