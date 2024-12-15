from fastapi import APIRouter
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider


router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream")
async def popular(id:int):
    try:
        # Retrieve the query string using the query manager
        query = query_manager.get_query("stream", "get_stream_data")        
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
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoSub = idSub["id_provider"]["idGogo"]
        gogoDub = idSub["id_provider"]["idGogoDub"]
        # https://anitaku.bz/blue-lock-vs-u-20-japan-dub-episode-6
        streamingEpisodes = data["streamingEpisodes"]
        episode_dataSub = []
        episode_dataDub = []

        # Loop through the length of streamingEpisodes sub
        for i in range(len(streamingEpisodes)):
            # Construct the URL dynamically for each episode
            url = f"https://anitaku.bz/{gogoSub}-episode-{i+1}"

            # Fetch and parse the episode data asynchronously
            md = parse_streaming_info(url)
            
            # Add the parsed data (md) to the result list
            episode_dataSub.append(md)

        # Loop through the length of streamingEpisodes dub
        for i in range(len(streamingEpisodes)):
            # Construct the URL dynamically for each episode
            url = f"https://anitaku.bz/{gogoDub}-episode-{i+1}"

            # Fetch and parse the episode data asynchronously
            md = parse_streaming_info(url)
            
            # Add the parsed data (md) to the result list
            episode_dataDub.append(md)

        mod = {
            "streamingEpisodesSub": episode_dataSub,
            "streamingEpisodesDub": episode_dataDub,
            "data":data
        }
        # Check for errors in the response
        if response.get("errors"):
            return {"error": response["errors"]}, 500
        
        # Get stream URL
        
        # Return the parsed result as JSON
        return {"result": mod}, 200

    except requests.exceptions.RequestException as e:
        # Handle any error with the request
        return {"error": str(e)}, 500

    except Exception as e:
        # Handle any unforeseen error
        return {"error": str(e)}, 500
