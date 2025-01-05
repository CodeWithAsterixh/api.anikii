import requests
from urllib.parse import urlparse


# Synchronous function to fetch mapping data
def fetch_mapping_data(anime_id: int):
    try:
        # Define the URL
        url = f"https://raw.githubusercontent.com/bal-mackup/mal-backup/master/anilist/anime/{anime_id}.json"
        
        # Make the GET request
        response = requests.get(url)
        # Raise an exception for HTTP errors
        response.raise_for_status()
        
        # Parse and return the JSON response
        return response.json()
    except requests.HTTPError as http_err:
        return {"error": f"HTTP error occurred: {http_err}"}
    except Exception as err:
        return {"error": f"An error occurred: {err}"}



# Define custom_provider_data here (as an example)
custom_provider_data = [
    {"id": 1, "idGogo": "gogo123", "idGogoDub": "gogoDub123", "idZoro": "zoro123", "idPahe": "pahe123"},
    {"id": 2, "idGogo": "gogo456", "idGogoDub": "gogoDub456", "idZoro": "zoro456", "idPahe": "pahe456"},
    # Add more entries as needed
]
# Async function to process the provider data
async def get_id_each_provider(json_data: dict, anime_id: int) -> dict:
    id_gogo = ""
    id_gogo_dub = ""
    id_zoro = ""
    id_pahe = ""

    # Iterate through each site in the JSON
    for anime_page, anime_info in json_data.get("Sites", {}).items():
        for anime_id_key, anime in anime_info.items(): 
            if anime_page == "Gogoanime":
                id_gogo = list(anime_info.values())[0].get("identifier", "")
                
                # Check if there is a second item in the list before accessing it
                if len(anime_info.values()) > 1 and list(anime_info.values())[1]:
                    id_gogo_dub = list(anime_info.values())[1].get("identifier", "")
                
            elif anime_page == "Zoro":
                id_zoro = urlparse(anime.get("url", "")).path.strip("/")
            elif anime_page == "animepahe":
                id_pahe = anime.get("identifier", "")

    # Check if the data is available in the customProviderData
    custom_provider_item = next(
        (item for item in custom_provider_data if item.get("id") == anime_id),
        None
    )

    if custom_provider_item:
        return {
            "idGogo": custom_provider_item.get("idGogo", ""),
            "idGogoDub": custom_provider_item.get("idGogoDub", ""),
            "idZoro": custom_provider_item.get("idZoro", ""),
            "idPahe": custom_provider_item.get("idPahe", ""),
        }
    else:
        return {
            "idGogo": id_gogo,
            "idGogoDub": id_gogo_dub,
            "idZoro": id_zoro,
            "idPahe": id_pahe,
        }

# Main function to fetch data and get provider IDs
async def fetch_malsyn_data_and_get_provider(anime_id: int):
    # Fetch the mapping data (remove await since this is synchronous)
    malsyn_data = fetch_mapping_data(anime_id)
    id_provider = None
    is_dub = False

    if not malsyn_data:
        id_provider = None
    else:
        # Get the provider IDs (await since this is async)
        id_provider = await get_id_each_provider(malsyn_data, anime_id)

        # Check if Gogoanime exists and contains "dub"
        if malsyn_data.get("Sites", {}).get("Gogoanime"):
            if "dub" in str(malsyn_data["Sites"]["Gogoanime"]):
                is_dub = True

    return {
        "id_provider": id_provider,
        "is_dub": is_dub,
    }
