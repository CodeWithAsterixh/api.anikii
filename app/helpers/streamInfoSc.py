import httpx
from bs4 import BeautifulSoup
from typing import List, Dict

from app.helpers.gogo_episodes import scrape_gogo_episode_list, get_highest_episode, get_max_episodes_from_gogo

# Define the types for the result (similar to your StreamInfo and StreamLink in TypeScript)
class StreamLink:
    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

class StreamInfo:
    def __init__(self, anime_info: Dict[str, str], episode_info: Dict[str, str], stream_links: List[StreamLink]):
        self.anime_info = anime_info
        self.episode_info = episode_info
        self.stream_links = stream_links

async def parse_streaming_info(url: str) -> StreamInfo:
    # Make a GET request to fetch the HTML content of the URL
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()  # Ensure the request was successful
        html = r.text
    
    # Parse the HTML content with BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Extract stream links (class and URL)
    stream_links = []
    for li in soup.select('div.anime_muti_link ul li'):
        name = li.get('class', [None])[0]  # Get the first class name (if exists)
        url_el = li.find('a', {'data-video': True})  # Find the link with the 'data-video' attribute
        if name and url_el:
            stream_links.append(StreamLink(name, url_el.get('data-video')))
    
    # Extract the maximum episode number from the page
    # Fallback to the new scraper for more accurate results if needed
    max_episode = await get_max_episodes_from_gogo(url, soup)
    
    # Extract anime information
    anime_info = {
        'title': soup.select_one('div.anime-info a[title]').text.strip() if soup.select_one('div.anime-info a[title]') else "Unknown",  # Extract the anime title
        'category': soup.select_one('div.anime_video_body_cate a[title]').text.strip() if soup.select_one('div.anime_video_body_cate a[title]') else "TV",  # Extract the category
        "episodes": max_episode
    }
    # Extract episode information
    episode_info = {
        'title': soup.select_one('.anime_video_body h1').text.split("at gogoanime")[0].strip() if soup.select_one('.anime_video_body h1') else "Episode"  # Clean episode title
    }

    # Return the result as a StreamInfo object
    return StreamInfo(anime_info, episode_info, stream_links)

# Example usage:
# streaming_info = await parse_streaming_info(url)


