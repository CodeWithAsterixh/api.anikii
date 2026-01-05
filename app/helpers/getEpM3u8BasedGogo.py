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

async def get_episode(id: str, ep: str) -> Optional[Dict]:
    """
    Scrapes episode data for a given anime ID, including name, episode count, streaming link, and servers.

    Args:
        id (str): The ID of the anime episode.
        ep (str): The episode number.
        name (str): The name of the anime.

    Returns:
        Optional[dict]: A dictionary containing the episode's information, or None if not found.
    """
    headers = {"User-Agent": USER_AGENT}

    for base_url in BASE_URLS:
        try:
            # Adjust the `id` based on the base_url
            if "www14.gogoanimes.fi" in base_url:
                print(id)
                # If base URL is www14.gogoanimes.fi, use the slug as provided
                # The id passed here is already a slug from romaji title (from fetch_malsyn_data_and_get_provider)
                formatted_id = f"{id}-episode-{ep}"
            elif "anitaku" in base_url:
                # If base URL is anitaku.bz, format id as "{id}-episode-{ep}"
                formatted_id = f"{id}-episode-{ep}"
            elif "gogoanime.co.at" in base_url:
                # If base URL is gogoanime.co.at, format id as "{id}-episode-{ep}-english-subbed"
                if "dub" not in id.lower():  # If it's not a dub, assume it's sub
                    formatted_id = f"{id}-episode-{ep}-english-subbed/"
                else:
                    formatted_id = f"{id}-episode-{ep}"
            else:
                # Default format for other base URLs (if needed)
                formatted_id = f"{id}-episode-{ep}"

            # Construct the episode link
            link = urljoin(base_url, formatted_id)

            # Fetch the page asynchronously
            async with httpx.AsyncClient() as client:
                response = await client.get(link, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to fetch {link}: {response.status_code}")
                    continue

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Scrape total episode count using the unified tool
            episode_count = await get_max_episodes_from_gogo(link, soup)

            # Scrape iframe URL
            iframe_elem = soup.select_one("div.player-embed iframe")
            iframe_url = iframe_elem.get("src") if iframe_elem and "src" in iframe_elem.attrs else None

            # Scrape server list with grouping (SUB/DUB/HSUB)
            servers = {}
            grouped_servers = {"SUB": {}, "DUB": {}, "HSUB": {}}
            
            # Find all server sections
            server_sections = soup.select("div.server-items")
            
            if server_sections:
                for section in server_sections:
                    data_type = section.get("data-type", "SUB").upper()
                    if data_type not in grouped_servers:
                        grouped_servers[data_type] = {}
                        
                    server_list = section.select("ul.muti_link li.server")
                    for server in server_list:
                        anchor = server.find("a")
                        if anchor and anchor.has_attr("data-video"):
                            video_url = anchor["data-video"]
                            if video_url.startswith("//"):
                                video_url = f"https:{video_url}"
                            
                            server_name = ""
                            for child in anchor.children:
                                if hasattr(child, 'name') and child.name not in ["span", "i"]:
                                    text = child.get_text(strip=True)
                                    if text:
                                        server_name = text
                                        break
                            
                            if not server_name:
                                # Fallback to first text content
                                server_name = anchor.find(text=True, recursive=False)
                                if server_name:
                                    server_name = server_name.strip()
                            
                            if not server_name:
                                server_name = "Unknown"
                                
                            grouped_servers[data_type][server_name] = video_url
                            # Keep backward compatibility for the first/default servers list
                            if server_name not in servers:
                                servers[server_name] = video_url
            else:
                # Fallback to legacy selectors
                server_list = soup.select("div.anime_muti_link ul li, ul.muti_link li")
                if server_list:
                    for server in server_list:
                        anchor = server.find("a")
                        if anchor and anchor.has_attr("data-video"):
                            video_url = anchor["data-video"]
                            if video_url.startswith("//"):
                                video_url = f"https:{video_url}"

                            server_name = ""
                            for child in anchor.children:
                                if hasattr(child, 'name') and child.name not in ["span", "i"]:
                                    text = child.get_text(strip=True)
                                    if text:
                                        server_name = text
                                        break
                            
                            if not server_name:
                                server_classes = server.get("class", [])
                                server_name = server_classes[0] if server_classes and server_classes[0] != "anime" else "Unknown"

                            servers[server_name] = video_url
                            # Assume legacy is SUB if not specified
                            grouped_servers["SUB"][server_name] = video_url

            if not servers and not any(grouped_servers.values()):
                print(f"No servers found for {link}")
                continue
            # Get M3U8 stream using iframe URL
            m3u8 = None
            # if iframe_url:
            #     try:
            #         m3u8 = await get_m3u8(iframe_url)  # Ensure `get_m3u8` is async
            #     except Exception as e:
            #         print(f"Error fetching M3U8: {e}")
            #         continue
                    

            # Scrape anime name
            name_elem = soup.select_one("div.anime_video_body h1")
            name = name_elem.text.replace("at gogoanime", "").strip() if name_elem else None

            # Compile results
            return {
                "name": name,
                "episodes": episode_count,
                "stream": m3u8,
                "servers": servers,
                "grouped_servers": grouped_servers,
            }

        except Exception as e:
            print(f"Error processing base URL {base_url}: {e}")
            continue

    # Return None if no data found from all base URLs
    print("No data found for the given ID across all base URLs.")
    return None
