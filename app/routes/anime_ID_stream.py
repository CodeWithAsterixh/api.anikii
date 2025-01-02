from fastapi import APIRouter, HTTPException
from app.helpers.fetchHelpers import make_api_request
from app.queries.query_manager import query_manager
from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
import requests

router = APIRouter(prefix="/anime", tags=["id"])

@router.get("/{id}/stream")
async def animeInfoStream(id: int):
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
        response = make_api_request(body)
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])
        data = response["data"]["Media"]
        # idSub = await fetch_malsyn_data_and_get_provider(id)
        # gogoSub = idSub["id_provider"]["idGogo"]
        # gogoDub = idSub["id_provider"]["idGogoDub"]

        # streamingEpisodes = data["episodes"]
        # episode_dataSub = []
        # episode_dataDub = []

        # # Loop through the length of streamingEpisodes (Sub)
        # for i in range(streamingEpisodes):
        #     try:
        #         # Construct the URL dynamically for each episode
        #         url = f"https://anitaku.bz/{gogoSub}-episode-{i+1}"
        #         # Fetch and parse the episode data asynchronously
        #         md = parse_streaming_info(url)
        #         episode_dataSub.append(md)
        #     except requests.exceptions.HTTPError as e:
        #         if e.response.status_code == 404:
        #             # Handle 404 error gracefully
        #             episode_dataSub.append({"error": "Episode not found", "episode": i + 1})
        #         else:
        #             raise  # Reraise for other HTTP errors

        # # Loop through the length of streamingEpisodes (Dub)
        # for i in range(streamingEpisodes):
        #     try:
        #         # Construct the URL dynamically for each episode
        #         url = f"https://anitaku.bz/{gogoDub}-episode-{i+1}"
        #         # Fetch and parse the episode data asynchronously
        #         md = parse_streaming_info(url)
        #         episode_dataDub.append(md)
        #     except requests.exceptions.HTTPError as e:
        #         if e.response.status_code == 404:
        #             # Handle 404 error gracefully
        #             episode_dataDub.append({"error": "Episode not found", "episode": i + 1})
        #         else:
        #             raise  # Reraise for other HTTP errors

        # mod = {
        #     "streamingEpisodesSub": episode_dataSub,
        #     "streamingEpisodesDub": episode_dataDub,
        #     "data": data
        # }

        # Check for errors in the response
        if response.get("errors"):
            raise HTTPException(status_code=500, detail=response["errors"])

        # Return the parsed result as JSON
        return {"result": data}, 200

    except requests.exceptions.RequestException as e:
        # Handle any general request errors
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")

    except Exception as e:
        # Handle any unforeseen errors
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
