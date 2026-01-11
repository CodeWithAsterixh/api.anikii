from urllib.parse import urlparse

# Synchronous function to fetch mapping data
# (Deprecated: no longer used for provider IDs)
# NOTE: Removed requests dependency to avoid blocking calls; function retained for reference.

# Define custom_provider_data here (as an example)
custom_provider_data = [
    {"id": 1, "idGogo": "gogo123", "idGogoDub": "gogoDub123", "idZoro": "zoro123", "idPahe": "pahe123"},
    {"id": 2, "idGogo": "gogo456", "idGogoDub": "gogoDub456", "idZoro": "zoro456", "idPahe": "pahe456"},
    # Add more entries as needed
]
# Async function to process the provider data
def get_id_each_provider(json_data: dict, anime_id: int) -> dict:
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

from app.services.anilist_media_service import fetch_anime_details
from app.helpers.base import slugify_anikii

# Main function to fetch data and get provider IDs
async def fetch_malsyn_data_and_get_provider(anime_id: int):
    """Build provider IDs using AniList details (English title prioritized, then romaji) instead of MAL backup.
    - idGogo: English title slug (lowercase, spaces -> hyphens)
    - idGogoDub: English title slug with '-dub' suffix
    - idZoro/idPahe: left empty
    """
    try:
        media = await fetch_anime_details(anime_id)
        title = media.get("title", {})
        # Prioritize English title as requested by user
        name = title.get("english") or title.get("romaji") or ""
        slug = slugify_anikii(name) if name else ""

        id_provider = {
            "idGogo": slug,
            "idGogoDub": f"{slug}" if slug else "",
            "idZoro": "",
            "idPahe": "",
        }

        # is_dub is no longer inferred from MAL backup; default False
        is_dub = False

        return {
            "id_provider": id_provider,
            "is_dub": is_dub,
        }
    except Exception:
        return {
            "id_provider": None,
            "is_dub": False,
        }
