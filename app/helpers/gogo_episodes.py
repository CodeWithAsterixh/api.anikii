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
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }
        
        try:
            client = await get_async_client()
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url}: {response.status_code}")
                return []
            html = response.text
            soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return []

    episodes = []
    
    # Both domains use #episode_related inside #load_ep
    ep_list_container = soup.select_one("#load_ep #episode_related")
    if not ep_list_container:
        # Fallback: sometimes it might be just #episode_related
        ep_list_container = soup.select_one("#episode_related")
        
    if not ep_list_container:
        return []
        
    for li in ep_list_container.find_all("li"):
        a_tag = li.find("a")
        if not a_tag:
            continue
            
        href = a_tag.get("href", "")
        
        # Extract episode number
        # gogoanimez.cc often has data-num
        ep_num = a_tag.get("data-num")
        
        # If not in data-num, look in div.name
        if not ep_num:
            name_div = a_tag.select_one(".name")
            if name_div:
                # Structure: <div class="name"><span>EP</span> 24</div>
                # Get text, replace 'EP' and strip
                text = name_div.get_text(separator=" ", strip=True)
                if "EP" in text.upper():
                    ep_num = text.upper().replace("EP", "").strip()
                else:
                    ep_num = text.strip()
        
        # Category (SUB/DUB)
        cate = "SUB"
        cate_div = a_tag.select_one(".cate")
        if cate_div:
            cate = cate_div.get_text(strip=True)
        elif a_tag.get("data-dub") == "1":
            cate = "DUB"
            
        # Title
        # gogoanimez.cc has title on li
        title = li.get("title") or ""
        
        # Some versions might have title inside the a tag or div.name
        if not title:
            title = a_tag.get("title") or ""
            
        episodes.append({
            "number": ep_num,
            "url": href,
            "category": cate,
            "title": title
        })
        
    return episodes

async def get_max_episodes_from_gogo(url: str, soup: Optional[BeautifulSoup] = None) -> int:
    """
    Unified tool to get the maximum episode number from a GogoAnime page.
    Prioritizes the #episode_page list to extract the highest episode number.
    """
    if not soup:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36"
        }
        try:
            client = await get_async_client()
            response = await client.get(url, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
        except Exception as e:
            logger.error(f"Error fetching {url} for max episodes: {e}")

    max_episode = 0

    # 1. Prioritize ul#episode_page which contains the ranges (e.g., 1101-1155)
    if soup:
        episode_page_ul = soup.select_one('ul#episode_page')
        if episode_page_ul:
            try:
                list_items = episode_page_ul.select('li')
                if list_items:
                    # Get the last li which contains the highest range
                    last_a = list_items[-1].find('a')
                    if last_a:
                        # Try ep_end attribute first (common on Gogo)
                        ep_end = last_a.get('ep_end')
                        if ep_end and ep_end.isdigit():
                            max_episode = int(ep_end)
                        else:
                            # Fallback: Parse from text or data-value (e.g., "1101-1155")
                            val = last_a.get('data-value') or last_a.get_text(strip=True)
                            if "-" in val:
                                max_episode = int(val.split("-")[-1])
                            elif val.isdigit():
                                max_episode = int(val)
            except (ValueError, TypeError, AttributeError, IndexError) as e:
                logger.warning(f"Error parsing episode_page: {e}")
                max_episode = 0

    # 2. Fallback to scraping the episode list if pagination wasn't helpful
    if max_episode == 0:
        scraped_episodes = await scrape_gogo_episode_list(url, soup)
        max_episode = get_highest_episode(scraped_episodes)
                
    return max_episode

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
