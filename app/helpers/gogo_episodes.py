import httpx
from bs4 import BeautifulSoup
from typing import List, Dict, Optional

async def scrape_gogo_episode_list(url: str) -> List[Dict]:
    """
    Scrapes the episode list from GogoAnime domains (gogoanimez.cc and gogoanimes.fi).
    Both use a similar structure for the episode list in the 'load_ep' section.
    """
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
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
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
