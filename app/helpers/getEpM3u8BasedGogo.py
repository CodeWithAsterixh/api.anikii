import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, Optional
from app.helpers.scrapers.m3u8Fetch import get_m3u8  # Replace with your `get_m3u8` implementation

# Constants
BASE_URLS = [
    "https://gogoanime.co.at",
    "https://anitaku.so",
    "https://gogoanime3.co",
    "https://gogoanimes.com.in/",
    "https://gogoanime.co.ba/"
]
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
)

def get_episode(id: str) -> Optional[Dict]:
    """
    Scrapes episode data for a given anime ID, including name, episode count, streaming link, and servers.

    Args:
        id (str): The ID of the anime episode.

    Returns:
        Optional[dict]: A dictionary containing the episode's information, or None if not found.
    """
    for base_url in BASE_URLS:
        try:
            # Construct the episode link
            link = urljoin(base_url, id)
            print(f"Trying URL: {link}")

            # Fetch the page
            response = requests.get(link, headers={"User-Agent": USER_AGENT})
            if response.status_code != 200:
                print(f"Failed to fetch {link}: {response.status_code}")
                continue

            html = response.text
            soup = BeautifulSoup(html, "html.parser")

            # Scrape episode count
            episode_count_elem = soup.select_one("ul#episode_page li a.active")
            episode_count = episode_count_elem["ep_end"] if episode_count_elem else None

            # Scrape iframe URL
            iframe_elem = soup.select_one("div.play-video iframe")
            iframe_url = iframe_elem["src"] if iframe_elem else None

            # Scrape server list
            server_list = soup.select("div.anime_muti_link ul li")
            servers = {
                server.get("class")[0]: server.find("a")["data-video"]
                for server in server_list
                if "anime" not in server.get("class", [])
            }

            # Get M3U8 stream using iframe URL
            m3u8 = None
            if iframe_url:
                try:
                    m3u8 = get_m3u8(iframe_url)
                except Exception as e:
                    print(f"Error fetching M3U8: {e}")

            # Scrape anime name
            name_elem = soup.select_one("div.anime_video_body h1")
            name = name_elem.text.replace("at gogoanime", "").strip() if name_elem else None

            # Compile results
            return {
                "name": name,
                "episodes": episode_count,
                "stream": m3u8,
                "servers": servers,
            }

        except Exception as e:
            print(f"Error processing base URL {base_url}: {e}")
            continue

    # Return None if no data found from all base URLs
    print("No data found for the given ID across all base URLs.")
    return None


