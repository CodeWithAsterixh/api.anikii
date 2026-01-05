import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

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
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=headers)
                if response.status_code != 200:
                    print(f"Failed to fetch {url}: {response.status_code}")
                    return []
                html = response.text
                soup = BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"Error fetching {url}: {e}")
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
    It tries scraping the episode list first, then falls back to the pagination metadata.
    """
    scraped_episodes = await scrape_gogo_episode_list(url, soup)
    max_episode = get_highest_episode(scraped_episodes)
    
    if max_episode == 0 and soup:
        max_ep_available = soup.select_one('ul#episode_page')
        if max_ep_available:
            try:
                # Find the last pagination link which usually has the end episode number
                last_li = max_ep_available.select('li')
                if last_li:
                    last_a = last_li[-1].find('a')
                    if last_a:
                        max_episode = int(last_a.get('ep_end', 0))
            except (ValueError, TypeError, AttributeError):
                max_episode = 0
                
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
