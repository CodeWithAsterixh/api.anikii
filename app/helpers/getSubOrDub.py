from fastapi import HTTPException
import urllib3
from app.helpers.getEpM3u8BasedGogo import get_episode

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL, slugify_anikii

async def get_episode_data(id: int, ep: int, type: str = "sub"):
    """
    Common helper to retrieve streaming info for an episode.
    Depending on the type ("sub" or "dub"), it fetches provider data and builds
    the appropriate URL, then parses the streaming info from that URL.
    """
    try:
        provider = await fetch_malsyn_data_and_get_provider(id)
        gogo_id = _extract_gogo_id(provider, type)
        if not gogo_id:
            return None

        url = f"{BASEURL}/{gogo_id}-episode-{ep}"
        data = await parse_streaming_info(url)

        extra_servers = await _fetch_extra_servers(gogo_id, ep)

        processed_links = _process_stream_links(data.stream_links)
        stream_links = _merge_servers(processed_links, extra_servers)

        return {
            "anime_info": data.anime_info,
            "episode_info": data.episode_info,
            "stream_links": stream_links,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")


def _extract_gogo_id(provider: dict, type: str) -> str | None:
    """Extract the appropriate gogo_id based on sub/dub type."""
    if type == "sub":
        return provider.get("id_provider", {}).get("idGogo")
    elif type == "dub":
        return provider.get("id_provider", {}).get("idGogoDub")
    else:
        raise HTTPException(status_code=400, detail="Invalid type parameter")


def _build_nineanime_url(data, ep: int, type: str) -> str | None:
    """Construct 9anime.org.lv episode URL from anime title slug."""
    anime_title = data.anime_info.get("title") if isinstance(data.anime_info, dict) else None
    if not anime_title:
        return None
    slug = slugify_anikii(anime_title)
    base = "https://9anime.org.lv"
    suffix = "-dub" if type == "dub" else ""
    return f"{base}/{slug}{suffix}-episode-{ep}"


async def _fetch_extra_servers(gogo_id: str, ep: int) -> dict:
    """Fetch extra server data from gogo."""
    episode_extra = await get_episode(gogo_id, ep)
    return episode_extra.get("servers", {}) if episode_extra else {}


def _process_stream_links(links) -> list[dict]:
    """Clean and filter streaming links."""
    processed = []
    for link in links:
        name, url = _get_name_url(link)
        if not url:
            continue
        url = _normalize_url(url)
        if _should_skip_link(name, url):
            continue
        processed.append({"name": name, "url": url})
    return processed


def _get_name_url(link):
    """Extract name and url from link object or dict."""
    if isinstance(link, dict):
        return link.get("name"), link.get("url")
    return getattr(link, "name", None), getattr(link, "url", None)


def _normalize_url(url: str) -> str:
    """Strip artifacts and ensure https prefix for protocol-relative URLs."""
    url = url.strip().strip("`").strip('"').strip("'")
    if url.startswith("//"):
        url = "https:" + url
    return url


def _should_skip_link(name, url: str) -> bool:
    """Return True if link should be excluded."""
    return (
        name == "anime"
        and (
            ("gogoanime.me.uk/newplayer.php" in url and ("type=hd-1" in url or "type=hd-2" in url))
            or "s3taku.com/streaming.php" in url
        )
    )


def _merge_servers(processed_links: list[dict], extra_servers: dict) -> list[dict]:
    """Merge processed links with extra servers, de-duplicating by URL."""
    final = {link["url"]: link for link in processed_links}
    for name, url in extra_servers.items():
        if url not in final:
            final[url] = {"name": name, "url": url}
    return list(final.values())
 