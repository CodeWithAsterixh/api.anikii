import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse


# Define a common browser user-agent string
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

# Your asynchronous video URL extractor function
async def getVid(url: str) -> str:
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
    # Regex to capture the video URL from the player.src call
    pattern = re.compile(
        r'player\.src\(\s*{\s*type:\s*"video/mp4",\s*src:\s*"([^"]+)"',
        re.DOTALL
    )
    for script in scripts:
        if script.string:
            match = pattern.search(script.string)
            if match:
                video_url = match.group(1)
                break

    if video_url:
        print("Found video URL:", video_url)
        return video_url
    else:
        print("Video URL not found")
        return None


