import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.helpers.security import is_safe_url


# Define a common browser user-agent string
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

# Your asynchronous video URL extractor function
async def getVid(url: str) -> str:
    if not is_safe_url(url):
        print(f"Blocked unsafe URL: {url}")
        return None
        
    parsed_url = urlparse(url)
    referer_url = parsed_url.geturl()
    print(f"Fetching URL: {referer_url}")

    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(referer_url, headers={"User-Agent": USER_AGENT})
        print("Response status:", r.status_code)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
    scripts = soup.find_all("script")
    video_url = None
    # Regex patterns to capture the video URL
    patterns = [
        re.compile(r'player\.src\(\s*{\s*type:\s*"video/mp4",\s*src:\s*"([^"]+)"', re.DOTALL),
        re.compile(r'src:\s*"([^"]+mp4)"', re.DOTALL),
        re.compile(r'source\s+src="([^"]+)"', re.DOTALL),
    ]
    
    for script in scripts:
        if script.string:
            for pattern in patterns:
                match = pattern.search(script.string)
                if match:
                    video_url = match.group(1)
                    if not video_url.startswith("http"):
                        # Handle protocol-relative URLs
                        if video_url.startswith("//"):
                            video_url = "https:" + video_url
                        else:
                            # Build absolute URL from base if needed
                            video_url = f"{parsed_url.scheme}://{parsed_url.netloc}/{video_url.lstrip('/')}"
                    break
            if video_url:
                break

    if video_url:
        print("Found video URL:", video_url)
        return video_url
    else:
        print("Video URL not found")
        return None


