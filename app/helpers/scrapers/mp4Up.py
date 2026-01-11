import re
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from app.helpers.security import is_safe_url


from app.core.logger import logger


# Define a common browser user-agent string
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

# Your asynchronous video URL extractor function
async def get_vid(url: str) -> str:
    if not is_safe_url(url):
        logger.warning(f"Blocked unsafe URL: {url}")
        return ""
    parsed_url = urlparse(url)
    referer_url = parsed_url.geturl()
    logger.debug(f"Fetching URL: {referer_url}")

    try:
        html = await _fetch_html(referer_url)
    except httpx.HTTPStatusError as e:
        logger.debug(f"HTTP error for {referer_url}: {e.response.status_code}")
        return ""

    video_url = _extract_video_url(html, parsed_url)
    if video_url:
        logger.debug(f"Found video URL: {video_url}")
        return video_url
    logger.debug(f"Video URL not found in {url}")
    return ""


async def _fetch_html(url: str) -> str:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        r = await client.get(url, headers={"User-Agent": USER_AGENT})
        logger.debug(f"Response status for {url}: {r.status_code}")
        r.raise_for_status()
        return r.text


def _extract_video_url(html: str, parsed_url) -> str | None:
    soup = BeautifulSoup(html, "html.parser")
    patterns = [
        re.compile(r'player\.src\(\s*{\s*type:\s*"video/mp4",\s*src:\s*"([^"]+)"', re.DOTALL),
        re.compile(r'src:\s*"([^"]+mp4)"', re.DOTALL),
        re.compile(r'source\s+src="([^"]+)"', re.DOTALL),
    ]
    for script in soup.find_all("script"):
        if not script.string:
            continue
        for pattern in patterns:
            match = pattern.search(script.string)
            if match:
                return _normalize_url(match.group(1), parsed_url)
    return None


def _normalize_url(video_url: str, parsed_url) -> str:
    if video_url.startswith("http"):
        return video_url
    if video_url.startswith("//"):
        return "https:" + video_url
    return f"{parsed_url.scheme}://{parsed_url.netloc}/{video_url.lstrip('/')}"

        


