from fastapi import APIRouter
from app.helpers.timeFunction import available_seasons,get_years


router = APIRouter()

@router.get("/")
async def home():
    # Message array split by periods
    message = [
        "Hello, there! Welcome to the Anikii API.",
        "See the available endpoints below to get data.",
        "Please maintain orderliness and respect while using this API.",
        "Please don't use the API for negative or harmful purposes."
    ]
    
    # Terms of Use and Code of Conduct
    terms_of_use = [
        "By using this API, you agree to comply with the Terms of Service and Code of Conduct.",
        "You are expected to use the data responsibly and respect the platform and community.",
        "Any misuse or abuse of the API may lead to suspension or banning of your access."
    ]
    
    
    # API Endpoints list with descriptions
    endpoints = [
        {"endpoint": "/popular", "description": "Fetch popular anime. Includes a page query (?page=number)."},
        {"endpoint": "/popular/upcoming", "description": "Fetch upcoming popular anime. Includes a page query (?page=number)."},
        {"endpoint": "/anime/{id}/", "description": "Fetch details of an anime by its ID. Includes a page query (?page=number)."},
        {"endpoint": "/anime/{id}/characters", "description": "Fetch characters of a specific anime. Includes a page query (?page=number)."},
        {"endpoint": "/anime/{id}/trailers", "description": "Fetch trailers of a specific anime."},
        {"endpoint": "/anime/{id}/recommended", "description": "Fetch recommended anime based on the anime ID. Includes a page query (?page=number)."},
        {"endpoint": "/anime/{id}/stream", "description": "Fetch streaming info for a specific anime."},
        {"endpoint": "/anime/{id}/stream/{ep}", "description": "Fetch streaming episode sub links for a specific anime."},
        {"endpoint": "/anime/{id}/stream/{ep}/dub", "description": "Fetch streaming episode dub links for a specific anime."},
        {"endpoint": "/anime/{id}/stream/{ep}/extra", "description": "Fetch extra streaming information for a specific anime episode."},
        {"endpoint": "/genres", "description": "Fetch all genres. Includes a page query (?page=number)."},
        {"endpoint": "/genres/{genre}", "description": "Fetch anime by genre. Includes a page query (?page=number)."},
        {"endpoint": "/popular/releases/", "description": "Fetch popular releases. Includes a page query (?page=number)."},
        {"endpoint": "/popular/releases/seasons", "description": "Fetch popular anime releases for current season. Includes a page query (?page=number)."},
        {"endpoint": "/popular/releases/seasons/{season}/{year}", "description": f"Fetch popular releases for a specific season within these seasons {available_seasons} and year within {get_years()}. Includes a page query (?page=number)."},
        {"endpoint": "/popular/releases/seasons/{season}", "description": f"Fetch popular anime releases for a specific season within these seasons {available_seasons}. Includes a page query (?page=number)."},
        {"endpoint": "/search", "description": "Search for anime based on keyword. Includes a keyword query (?keyword=search_string)."},
        {"endpoint": "/anime/{id}/stream/ep/{ep}/extra", "description": "Fetch extra streaming episode for a specific anime. Includes page query (?page=number)."}
    ]
    
    # Live URL
    live_url = "https://api-anikii.onrender.com/"
    
    return {
        "message": message,
        "terms_of_use": terms_of_use,
        "endpoints": endpoints,
        "liveurl": live_url
    }
