import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
from app.helpers.fetchHelpers import get_async_client
from app.core.logger import logger

async def scrape_gogo_episode_list(url: str, soup: Optional[BeautifulSoup] = None) -> List[Dict]:
    """
    Scrapes the episode list from GogoAnime domains (gogoanimez.cc and gogoanimes.fi).
    Both use a similar structure for the episode list in the 'load_ep' section.
    """
    if not soup:
        soup = await _fetch_soup(url)
        if not soup:
            return []

    ep_list_container = _get_episode_container(soup)
    if not ep_list_container:
        return []

    episodes = []
    for li in ep_list_container.find_all("li"):
        ep_data = _extract_episode_data(li)
        if ep_data:
            episodes.append(ep_data)
    return episodes


async def _fetch_soup(url: str) -> Optional[BeautifulSoup]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
    try:
        client = await get_async_client()
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            logger.warning(f"Failed to fetch {url}: {response.status_code}")
            return None
        return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.error(f"Error fetching {url}: {e}")
        return None


def _get_episode_container(soup: BeautifulSoup) -> Optional[BeautifulSoup]:
    container = soup.select_one("#load_ep #episode_related")
    if not container:
        container = soup.select_one("#episode_related")
    return container


def _extract_episode_data(li) -> Optional[Dict]:
    a_tag = li.find("a")
    if not a_tag:
        return None

    href = a_tag.get("href", "")
    ep_num = _extract_episode_number(a_tag)
    cate = _extract_category(a_tag)
    title = _extract_title(li, a_tag)

    return {
        "number": ep_num,
        "url": href,
        "category": cate,
        "title": title
    }


def _extract_episode_number(a_tag) -> str:
    ep_num = a_tag.get("data-num")
    if ep_num:
        return ep_num

    name_div = a_tag.select_one(".name")
    if not name_div:
        return ""

    text = name_div.get_text(separator=" ", strip=True).upper()
    if "EP" in text:
        return text.replace("EP", "").strip()
    return text.strip()


def _extract_category(a_tag) -> str:
    cate_div = a_tag.select_one(".cate")
    if cate_div:
        return cate_div.get_text(strip=True)
    if a_tag.get("data-dub") == "1":
        return "DUB"
    return "SUB"


def _extract_title(li, a_tag) -> str:
    return li.get("title") or a_tag.get("title") or ""
    

async def get_max_episodes_from_gogo(url: str, soup: Optional[BeautifulSoup] = None) -> int:
    """
    Unified tool to get the maximum episode number from a GogoAnime page.
    Prioritizes the #episode_page list to extract the highest episode number.
    """
    soup = soup or await _fetch_soup_for_max_episodes(url)
    if not soup:
        return 0

    max_episode = _try_get_max_from_episode_page(soup)
    if max_episode:
        return max_episode

    scraped_episodes = await scrape_gogo_episode_list(url, soup)
    return get_highest_episode(scraped_episodes)


async def _fetch_soup_for_max_episodes(url: str) -> Optional[BeautifulSoup]:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
    }
    try:
        client = await get_async_client()
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            return BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.error(f"Error fetching {url} for max episodes: {e}")
    return None


def _try_get_max_from_episode_page(soup: BeautifulSoup) -> int:
    episode_page_ul = soup.select_one('ul#episode_page')
    if not episode_page_ul:
        return 0

    last_li = episode_page_ul.select('li')[-1] if episode_page_ul.select('li') else None
    if not last_li:
        return 0

    last_a = last_li.find('a')
    if not last_a:
        return 0

    # Try ep_end attribute first (common on Gogo)
    ep_end = last_a.get('ep_end')
    if ep_end and ep_end.isdigit():
        return int(ep_end)

    # Fallback: Parse from text or data-value (e.g., "1101-1155")
    val = last_a.get('data-value') or last_a.get_text(strip=True)
    if "-" in val:
        try:
            return int(val.split("-")[-1])
        except ValueError:
            pass
    if val.isdigit():
        return int(val)

    return 0
    

def get_highest_episode(episodes: List[Dict]) -> int:
    """
    Extracts the highest episode number from a list of scraped episodes.
    """
    if not episodes:
        return 0
    
    highest = 0
    for ep in episodes:
        try:
            num_str = str(ep.get("number", "0")).strip()
            # Handle ranges or non-numeric if necessary, but usually it's a number
            if "-" in num_str:
                num = int(num_str.split("-")[-1])
            else:
                num = int(float(num_str))
            if num > highest:
                highest = num
        except (ValueError, TypeError):
            continue
            
    return highest
