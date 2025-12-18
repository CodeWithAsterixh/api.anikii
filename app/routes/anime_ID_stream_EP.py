import logging
import re
from typing import Optional
from urllib.parse import urlparse

import requests
import urllib3
# Removed direct anime_downloader import to enforce separation of concerns
from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from app.helpers.getSubOrDub import get_episode_data
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.scrapers.mp4Up import getVid
from app.services.anilist_service import fetch_anime_details
from app.services.anime_downloader_service import resolve_stream_with_anime_downloader
from app.helpers.response_envelope import success_response, error_response

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/anime", tags=["id", "ep"])


# Helper: Try resolving stream data using anime-downloader first, fallback to scraper
# async def resolve_stream_with_anime_downloader(anilist_id: int, ep: int, type_: str, provider_override: Optional[str] = None):
#     # moved to app.services.anime_downloader_service
#     try:
#         data = fetch_anime_details(anilist_id)
#         title_obj = data.get("title", {})
#         title = (
#             title_obj.get("english")
#             or title_obj.get("romaji")
#             or title_obj.get("native")
#         )
#         if not title:
#             return None

#         # First, try using MalSync mapped provider URLs to avoid search mismatches
#         try:
#             malsync_map = await fetch_malsyn_data_and_get_provider(anilist_id)
#             id_provider = (malsync_map or {}).get("id_provider") or {}
#         except Exception as e:
#             logger.debug(f"MalSync mapping fetch error: {e}")
#             id_provider = {}
#         is_dub = type_.lower() == "dub"
#         # Build direct URLs from mapping when available
#         mapped_candidates = []
#         # Determine provider preference order
#         provider_order = (
#             [provider_override]
#             if provider_override
#             else ["gogoanime", "animepahe", "9anime", "twistmoe"]
#         )
#         for prov in provider_order:
#             try:
#                 if prov == "gogoanime":
#                     slug = (
#                         id_provider.get("idGogoDub")
#                         if is_dub and id_provider.get("idGogoDub")
#                         else id_provider.get("idGogo")
#                     )
#                     if slug:
#                         for base in ["https://gogoanimes.cv", "https://gogoanimee.my"]:
#                             mapped_candidates.append(
#                                 {
#                                     "provider": "gogoanime",
#                                     "url": f"{base}/category/{slug}",
#                                 }
#                             )

#                 elif prov == "animepahe":
#                     pahe_id = id_provider.get("idPahe")
#                     if pahe_id:
#                         mapped_candidates.append(
#                             {
#                                 "provider": "animepahe",
#                                 "url": f"https://animepahe.com/anime/{pahe_id}",
#                             }
#                         )
#                 # 9anime and twistmoe are search-only here since MalSync mapping isn't extracted for them in modules.py
#             except Exception:
#                 continue
#         # Try mapped URLs first
#         for cand in mapped_candidates:
#             try:
#                 cls = get_anime_class(cand["provider"])
#                 anime_obj = cls(cand["url"])
#                 episodes = getattr(anime_obj, "episodes", [])
#                 logger.debug(
#                     f"MalSync {cand['provider']} object has {len(episodes)} episodes for URL {cand['url']}"
#                 )
#                 if not episodes:
#                     continue
#                 target = None
#                 for e in episodes:
#                     eno = getattr(e, "ep_no", None)
#                     if eno is not None and int(eno) == int(ep):
#                         target = e
#                         break
#                 if target is None and len(episodes) >= ep:
#                     target = episodes[ep - 1]
#                 if not target:
#                     continue
#                 stream_url = getattr(target, "stream_url", None)
#                 if not stream_url:
#                     continue
#                 episode_info = {
#                     "title": getattr(target, "pretty_title", f"{title}-{ep}"),
#                     "ep_no": getattr(target, "ep_no", ep),
#                 }
#                 logger.info(
#                     f"Resolved direct stream via mapped {cand['provider']} for id={anilist_id} ep={ep}: {stream_url}"
#                 )
#                 return {
#                     "episode_info": episode_info,
#                     "provider": cand["provider"],
#                     "stream_links": [{"name": "direct", "url": stream_url}],
#                 }
#             except Exception as e:
#                 logger.debug(f"Error resolving via mapped URL {cand}: {e}")
#                 continue

#         def sanitize_query(q: str) -> str:
#             # remove content inside parentheses and brackets
#             q = re.sub(r"\([^)]*\)", "", q)
#             q = re.sub(r"\[[^]]*\]", "", q)
#             # remove punctuation except spaces and hyphens
#             q = re.sub(r"[^\w\s-]", "", q)
#             # normalize spaces
#             q = re.sub(r"\s+", " ", q).strip()
#             return q

#         # Build candidate queries (handle dub heuristics across providers)
#         synonyms_list = data.get("synonyms", []) or []
#         base_queries = [title] + synonyms_list

#         # Prefer slug-based queries derived from English/Romaji titles
#         anikii_id_eng = None
#         anikii_id_rom = None
#         try:
#             from app.helpers.base import slugify_anikii

#             eng = title_obj.get("english") or ""
#             rom = title_obj.get("romaji") or ""
#             anikii_id_eng = slugify_anikii(eng) if eng else None
#             anikii_id_rom = slugify_anikii(rom) if rom else None
#         except Exception:
#             pass
#         preferred_queries = [q for q in [anikii_id_eng, anikii_id_rom] if q]

#         # Add sanitized variants and common season forms
#         season_forms = []
#         m = re.search(r"(Season|Cour|Part)\s*(\d)", title, flags=re.IGNORECASE)
#         if m:
#             num = m.group(2)
#             season_forms = [
#                 f"{sanitize_query(title)} {num}",
#                 f"{sanitize_query(title)} S{num}",
#                 f"{sanitize_query(title)} {num}nd",
#                 f"{sanitize_query(title)} {num}th",
#             ]
#         queries = preferred_queries.copy()
#         for bq in base_queries:
#             queries.append(bq)
#             sq = sanitize_query(bq)
#             if sq and sq != bq:
#                 queries.append(sq)
#         queries.extend(season_forms)
#         if is_dub:
#             suffixes = [" dub", " (Dub)", " english dub", " [Dub]", " - Dub"]
#             dub_queries = []
#             for q in queries:
#                 dub_queries.append(q)
#                 for s in suffixes:
#                     dq = f"{q}{s}"
#                     if dq not in dub_queries:
#                         dub_queries.append(dq)
#             queries = dub_queries
#         logger.debug(
#             f"anime-downloader queries built (slug-first) for id={anilist_id}, ep={ep}, type={type_}: {queries[:5]}... total={len(queries)}"
#         )

#         # Try multiple providers supported by anime-downloader
#         providers = (
#             [provider_override]
#             if provider_override
#             else ["gogoanime", "9anime", "animepahe", "twistmoe"]
#         )
#         for provider in providers:
#             try:
#                 cls = get_anime_class(provider)
#                 search_results = []
#                 for q in queries:
#                     try:
#                         res = cls.search(q) or []
#                         if res:
#                             search_results = res
#                             logger.debug(
#                                 f"Provider {provider} matched query '{q}' with {len(res)} results"
#                             )
#                             break
#                     except Exception as e:
#                         logger.debug(
#                             f"Provider {provider} search error for query '{q}': {e}"
#                         )
#                         continue
#                 if not search_results:
#                     logger.debug(f"Provider {provider} had no search results")
#                     continue
#                 # Choose a result whose episode list covers requested ep, otherwise pick the one with max episodes
#                 chosen_stub = None
#                 max_eps = -1
#                 for stub in search_results:
#                     try:
#                         obj = stub.__class__(stub.url)
#                         eps = getattr(obj, "episodes", [])
#                         if eps:
#                             if len(eps) >= ep and chosen_stub is None:
#                                 chosen_stub = stub
#                                 logger.debug(
#                                     f"Provider {provider} chose stub covering ep {ep}: {stub.url} with {len(eps)} eps"
#                                 )
#                                 break
#                             if len(eps) > max_eps:
#                                 max_eps = len(eps)
#                                 chosen_stub = stub
#                     except Exception as e:
#                         logger.debug(
#                             f"Provider {provider} error creating object from stub {getattr(stub, 'url', '')}: {e}"
#                         )
#                         continue
#                 if not chosen_stub:
#                     chosen_stub = search_results[0]
#                 anime_obj = chosen_stub.__class__(chosen_stub.url)
#                 episodes = getattr(anime_obj, "episodes", [])
#                 logger.debug(
#                     f"Provider {provider} selected anime has {len(episodes)} episodes"
#                 )
#                 if not episodes:
#                     continue
#                 target = None
#                 # Prefer matching ep_no if available
#                 for e in episodes:
#                     eno = getattr(e, "ep_no", None)
#                     if eno is not None and int(eno) == int(ep):
#                         target = e
#                         break
#                 # Fallback to index if ep_no matching failed
#                 if target is None and len(episodes) >= ep:
#                     target = episodes[ep - 1]
#                 if not target:
#                     logger.debug(
#                         f"Provider {provider} did not find target episode {ep}"
#                     )
#                     continue
#                 stream_url = getattr(target, "stream_url", None)
#                 if not stream_url:
#                     logger.debug(
#                         f"Provider {provider} target episode has no stream_url"
#                     )
#                     continue
#                 episode_info = {
#                     "title": getattr(target, "pretty_title", f"{title}-{ep}"),
#                     "ep_no": getattr(target, "ep_no", ep),
#                 }
#                 logger.info(
#                     f"Resolved direct stream via {provider} for id={anilist_id} ep={ep}: {stream_url}"
#                 )
#                 return {
#                     "episode_info": episode_info,
#                     "provider": provider,
#                     "stream_links": [{"name": "direct", "url": stream_url}],
#                 }
#             except Exception as e:
#                 logger.debug(f"Provider {provider} resolution error: {e}")
#                 # Try next provider on failure
#                 continue
#         logger.info(
#             f"anime-downloader failed to resolve stream for id={anilist_id} ep={ep} type={type_} override={provider_override}"
#         )
#         return None
#     except Exception as e:
#         print(e)
#         logger.error(f"Unexpected error in resolve_stream_with_anime_downloader: {e}")
#         return None


# Endpoint to fetch streaming info (sub/dub) for an episode.
@router.get("/{id}/stream/ep/{ep}")
async def stream_episode(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
):
    try:
        episode_data = await get_episode_data(id, ep, type)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to fetch episode data")
        return error_response(request, status_code=status_code, message=detail, error=str(e))
    return success_response(request, data=episode_data)


# Download endpoint that streams the original video and returns its original size.
@router.get("/{id}/stream/ep/{ep}/download")
async def download_streaming_video(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
):
    try:
        episode_data = await get_episode_data(id, ep, type)
    except Exception as e:
        status_code = getattr(e, "status_code", 500)
        detail = getattr(e, "detail", "Failed to fetch episode data")
        return error_response(request, status_code=status_code, message=detail, error=str(e))
    if not episode_data:
        return error_response(request, status_code=404, message="Episode not found")

    # Extract the mp4upload link from the stream_links list.
    mp4upload_link = next(
        (link.url for link in episode_data["stream_links"] if link.name == "mp4upload"),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="mp4upload link not found")

    # Use getVid to extract the direct video URL.
    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    try:
        r = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        r.raise_for_status()
    except Exception as e:
        return error_response(request, status_code=500, message="Error fetching video", error=str(e))

    # Include the Content-Length header if available.
    content_length = r.headers.get("Content-Length")
    extra_headers = {
        "Content-Disposition": f"attachment; filename={episode_data['episode_info']['title']}.mp4",
    }
    if content_length:
        extra_headers["Content-Length"] = content_length

    def iter_content():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_content(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
        headers=extra_headers,
    )


# Download direct stream with query params
@router.get("/{id}/stream/ep/{ep}/download-direct")
async def download_direct_stream(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
    provider: Optional[str] = Query(
        None,
        description="Optional provider override: gogoanime, 9anime, animepahe, twistmoe",
    ),
    episodes: Optional[str] = Query(
        None, description="Range of episodes in format <start>:<end> (e.g., '1:5')"
    ),
    quality: Optional[str] = Query(
        "720p", description="Quality of the episode (e.g., 360p, 480p, 720p, 1080p)"
    ),
    force_download: Optional[bool] = Query(
        False, description="Force download even if file exists"
    ),
    file_format: Optional[str] = Query(None, description="Format for naming the files"),
    skip_fillers: Optional[bool] = Query(
        False, description="Skip downloading filler episodes"
    ),
    fallback_qualities: Optional[str] = Query(
        None, description="Order of fallback qualities (e.g., 480p, 360p)"
    ),
    external_downloader: Optional[str] = Query(
        None, description="Use an external downloader like aria2c"
    ),
    disable_ssl: Optional[bool] = Query(
        False, description="Disable SSL verification for the download"
    ),
):
    print("go")
    # First, try anime-downloader for a direct stream URL
    episode_data = await resolve_stream_with_anime_downloader(
        id, ep, type, provider_override=provider
    )

    if not episode_data:
        try:
            episode_data = await get_episode_data(id, ep, type)
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            detail = getattr(e, "detail", "Failed to fetch episode data")
            return error_response(request, status_code=status_code, message=detail, error=str(e))
    # If no episode data is found, raise a 404
    if not episode_data:
        logger.warning(
            f"Episode not found for id={id}, ep={ep}, type={type}, provider={provider}"
        )
        return error_response(request, status_code=404, message="Episode not found")

    # Prefer direct link resolved by anime-downloader if present
    direct_link = next(
        (
            link["url"]
            for link in episode_data.get("stream_links", [])
            if link.get("name") == "direct"
        ),
        None,
    )

    if direct_link:
        headers = {"User-Agent": USER_AGENT}
        # Add referer header from direct link origin if available
        try:
            u = urlparse(direct_link)
            if u.scheme and u.netloc:
                headers["Referer"] = f"{u.scheme}://{u.netloc}/"
        except Exception:
            pass

        # Try fetching the video file directly from the link
        try:
            r = requests.get(
                direct_link,
                headers=headers,
                stream=True,
                timeout=30,
                verify=not disable_ssl,
            )
            r.raise_for_status()
        except Exception as e:
            logger.error(f"Error fetching video: {e}")
            return error_response(request, status_code=500, message="Error fetching video", error=str(e))

        # Get content length if available
        content_length = r.headers.get("Content-Length")
        extra_headers = {
            "Content-Disposition": f"attachment; filename={episode_data['episode_info']['title']}.mp4"
        }
        if content_length:
            extra_headers["Content-Length"] = content_length

        # Stream content back to the client
        def iter_content():
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

        return StreamingResponse(
            iter_content(),
            media_type=r.headers.get("Content-Type", "application/octet-stream"),
            headers=extra_headers,
        )

    # Fallback: Use mp4upload link resolution if direct link is unavailable
    mp4upload_link = next(
        (
            link.url
            for link in episode_data["stream_links"]
            if getattr(link, "name", None) == "mp4upload"
        ),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="No suitable stream link found")

    # Use mp4upload helper to resolve video URL
    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    # Try fetching video from the resolved link
    try:
        r = requests.get(
            video_url, headers=headers, stream=True, timeout=30, verify=not disable_ssl
        )
        r.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching video: {e}")
        return error_response(request, status_code=500, message="Error fetching video", error=str(e))

    content_length = r.headers.get("Content-Length")
    extra_headers = {
        "Content-Disposition": f"attachment; filename={episode_data['episode_info']['title']}.mp4"
    }
    if content_length:
        extra_headers["Content-Length"] = content_length

    # Stream content back to the client
    def iter_content():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_content(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
        headers=extra_headers,
    )


# Live streaming endpoint for an episode.
@router.get("/{id}/stream/ep/{ep}/live")
async def live_streaming_video(
    request: Request,
    id: int,
    ep: int,
    type: str = Query("sub", description="Type of episode: 'sub' or 'dub'"),
    provider: Optional[str] = Query(
        None,
        description="Optional provider override: gogoanime, 9anime, animepahe, twistmoe",
    ),
):
    episode_data = await resolve_stream_with_anime_downloader(
        id, ep, type, provider_override=provider
    )
    if not episode_data:
        try:
            episode_data = await get_episode_data(id, ep, type)
        except Exception as e:
            status_code = getattr(e, "status_code", 500)
            detail = getattr(e, "detail", "Failed to fetch episode data")
            return error_response(request, status_code=status_code, message=detail, error=str(e))
    if not episode_data:
        return error_response(request, status_code=404, message="Episode not found")

    # Extract the mp4upload link.
    mp4upload_link = next(
        (link.url for link in episode_data["stream_links"] if link.name == "mp4upload"),
        None,
    )
    if not mp4upload_link:
        return error_response(request, status_code=404, message="mp4upload link not found")

    video_url = await getVid(mp4upload_link)
    if not video_url:
        return error_response(request, status_code=500, message="Failed to extract video URL")

    headers = {"User-Agent": USER_AGENT, "Referer": mp4upload_link}

    try:
        r = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
        r.raise_for_status()
    except Exception as e:
        return error_response(request, status_code=500, message="Error fetching live stream", error=str(e))

    def iter_live():
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                yield chunk

    return StreamingResponse(
        iter_live(),
        media_type=r.headers.get("Content-Type", "application/octet-stream"),
    )
