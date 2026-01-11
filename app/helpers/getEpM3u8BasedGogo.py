import httpx  # Replace `requests` with `httpx`
from app.helpers.gogo_episodes import get_max_episodes_from_gogo
from bs4 import BeautifulSoup
import httpx
from urllib.parse import urljoin
from typing import Dict, Optional
from app.helpers.scrapers.m3u8Fetch import get_m3u8  # Ensure this is async

# Constants
BASE_URLS = [
    "https://gogoanimez.cc/watch/",
    "https://www14.gogoanimes.fi/",
    "https://gogoanime.co.at/",
    "https://anitaku.bz/",
    "https://gogoanime3.cc/",
    "https://9anime.org.lv/",
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
)

def _format_episode_url(base_url: str, id: str, ep: str) -> str:
    """Formats the episode URL based on the provider."""
    if "www14.gogoanimes.fi" in base_url or "anitaku" in base_url:
        formatted_id = f"{id}-episode-{ep}"
    elif "gogoanime.co.at" in base_url:
        if "dub" not in id.lower():
            formatted_id = f"{id}-episode-{ep}-english-subbed/"
        else:
            formatted_id = f"{id}-episode-{ep}"
    else:
        formatted_id = f"{id}-episode-{ep}"
    
    return urljoin(base_url, formatted_id)


def _get_server_name(anchor, server_item=None) -> str:
    """Extracts server name from anchor or fallback to server item classes."""
    server_name = _extract_from_children(anchor)
    if not server_name:
        server_name = _extract_from_anchor_text(anchor)
    if not server_name and server_item:
        server_name = _extract_from_server_item(server_item)
    return server_name or "Unknown"


def _extract_from_children(anchor):
    for child in anchor.children:
        if hasattr(child, 'name') and child.name not in ["span", "i"]:
            text = child.get_text(strip=True)
            if text:
                return text
    return ""


def _extract_from_anchor_text(anchor):
    text = anchor.find(text=True, recursive=False)
    return text.strip() if text else ""


def _extract_from_server_item(server_item):
    classes = server_item.get("class", [])
    return classes[0] if classes and classes[0] != "anime" else "Unknown"

def _extract_servers(soup: BeautifulSoup):
    """Scrapes server list with grouping (SUB/DUB/HSUB)."""
    servers = {}
    grouped_servers = {"SUB": {}, "DUB": {}, "HSUB": {}}

    server_sections = soup.select("div.server-items")
    if server_sections:
        _process_server_sections(server_sections, grouped_servers, servers)
    else:
        _process_legacy_servers(soup, grouped_servers, servers)

    return servers, grouped_servers


def _process_server_sections(server_sections, grouped_servers, servers):
    """Process modern server sections."""
    for section in server_sections:
        data_type = section.get("data-type", "SUB").upper()
        if data_type not in grouped_servers:
            grouped_servers[data_type] = {}

        for server in section.select("ul.muti_link li.server"):
            anchor = server.find("a")
            if not anchor or not anchor.has_attr("data-video"):
                continue

            video_url = _normalize_video_url(anchor["data-video"])
            server_name = _get_server_name(anchor)

            grouped_servers[data_type][server_name] = video_url
            if server_name not in servers:
                servers[server_name] = video_url


def _process_legacy_servers(soup, grouped_servers, servers):
    """Process legacy server list."""
    server_list = soup.select("div.anime_muti_link ul li, ul.muti_link li")
    for server in server_list:
        anchor = server.find("a")
        if not anchor or not anchor.has_attr("data-video"):
            continue

        video_url = _normalize_video_url(anchor["data-video"])
        server_name = _get_server_name(anchor, server)

        servers[server_name] = video_url
        grouped_servers["SUB"][server_name] = video_url


def _normalize_video_url(url: str) -> str:
    """Normalize video URL by adding https: if needed."""
    return f"https:{url}" if url.startswith("//") else url
    


async def get_episode(id: str, ep: str) -> Optional[Dict]:
    """
    Scrapes episode data for a given anime ID, including name, episode count, streaming link, and servers.

    Args:
        id (str): The ID of the anime episode.
        ep (str): The episode number.

    Returns:
        Optional[dict]: A dictionary containing the episode's information, or None if not found.
    """
    headers = {"User-Agent": USER_AGENT}

    for base_url in BASE_URLS:
        try:
            link = _format_episode_url(base_url, id, ep)

            async with httpx.AsyncClient() as client:
                response = await client.get(link, headers=headers)
                if response.status_code != 200:
                    continue

            soup = BeautifulSoup(response.text, "html.parser")
            episode_count = await get_max_episodes_from_gogo(link, soup)
            servers, grouped_servers = _extract_servers(soup)

            if not servers and not any(grouped_servers.values()):
                continue

            name_elem = soup.select_one("div.anime_video_body h1")
            name = name_elem.text.replace("at gogoanime", "").strip() if name_elem else None

            return {
                "name": name,
                "episodes": episode_count,
                "stream": None,
                "servers": servers,
                "grouped_servers": grouped_servers,
            }

        except Exception as e:
            print(f"Error processing base URL {base_url}: {e}")
            continue

    return None
