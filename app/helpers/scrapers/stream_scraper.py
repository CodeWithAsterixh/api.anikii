import httpx
from bs4 import BeautifulSoup
from app.helpers.security import is_safe_url
from app.helpers.base import substring_after, substring_before
from app.helpers.scrapers.crypto_utils import decrypt_sources
from app.helpers.fetchHelpers import get_async_client
from app.core.config import get_settings
from app.core.logger import logger

settings = get_settings()
BASE_URL = settings.BASE_URL_HIANIME

def retrieve_server_id(soup, index, sub_or_dub):
    servers = soup.select(f"div.ps_-block.ps_-block-sub.servers-{sub_or_dub} > div.ps__-list > div")
    for server in servers:
        if server.get("data-server-id") == str(index):
            return server.get("data-id")
    return None

async def extract_vidcloud(url):
    if not is_safe_url(url):
        logger.warning(f"Blocked unsafe vidcloud URL: {url}")
        return {"sources": [], "subtitles": []}
        
    host = "https://megacloud.tv"
    video_id = url.split("/")[-1].split("?")[0]

    client = await get_async_client()
    # Fetch sources
    response = await client.get(f"{host}/embed-2/ajax/e-1/getSources?id={video_id}", headers={"X-Requested-With": "XMLHttpRequest"})
    req_data = response.json()
    sources = req_data.get("sources")
    tracks = req_data.get("tracks", [])
    intro = req_data.get("intro", {})
    outro = req_data.get("outro", {})

    # Fetch decryption key
    decryption_key_resp = (await client.get("https://zorotv.com.in/key/6")).json()
    decryption_key = decryption_key_resp.get("key")

    # Decrypt sources
    if sources:
        decrypted_sources = decrypt_sources(sources, decryption_key)
    else:
        decrypted_sources = []

    result = {
        "sources": [],
        "subtitles": [{"url": track["file"], "lang": track.get("label", "Unknown")} for track in tracks],
        "intro": intro if intro.get("end", 0) > 1 else None,
        "outro": outro if outro.get("end", 0) > 1 else None
    }

    # Process HLS sources
    for source in decrypted_sources:
        if source["type"] == "hls":
            data = (await client.get(source["file"])).text
            resolutions = [line for line in data.split("\n") if "RESOLUTION" in line]
            for res in resolutions:
                quality = res.split(",")[0].split("x")[1].strip()
                result["sources"].append({"url": source["file"], quality: f"{quality}p"})

    return result

async def get_stream(episode_id, server="vidcloud"):
    if "$episode$" not in episode_id:
        raise ValueError("Invalid episode id")

    sub_or_dub = "dub" if "dub" in episode_id.split("$")[-1] else "sub"
    episode_id = f"{BASE_URL}/watch/{episode_id.replace('$episode$', '?ep=').replace('$auto', '').replace('$sub', '').replace('$dub', '')}"

    try:
        episode_number = substring_after(episode_id, "?ep=")
        client = await get_async_client()
        # Fetch episode servers
        response = await client.get(f"{BASE_URL}/ajax/v2/episode/servers?episodeId={episode_number}")
        soup = BeautifulSoup(response.json().get("html", ""), "html.parser")

        # Retrieve server ID
        server_id = retrieve_server_id(soup, 1, sub_or_dub)
        if not server_id:
            raise ValueError("RapidCloud server not found")

        # Fetch streaming link
        link_resp = await client.get(f"{BASE_URL}/ajax/v2/episode/sources?id={server_id}")
        streaming_link = link_resp.json().get("link")

        # Extract video sources
        return await extract_vidcloud(streaming_link)

    except Exception as e:
        logger.error(f"Error fetching stream: {e}")
        raise RuntimeError(f"Error fetching stream: {e}")
