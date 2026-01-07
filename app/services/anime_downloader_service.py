import logging
from typing import Optional, Dict, Any
from anime_downloader.sites import get_anime_class

from app.services.anilist_media_service import fetch_anime_details
from app.services.downloader_utils import _build_search_queries
from app.services.downloader_mapper import _get_mapped_candidates, _resolve_via_mapped_urls

logger = logging.getLogger(__name__)

async def resolve_stream_with_anime_downloader(anilist_id: int, ep: int, type_: str, provider_override: Optional[str] = None):
    """
    Resolve a stream for a given AniList ID and episode using anime-downloader providers.
    """
    try:
        data = await fetch_anime_details(anilist_id)
        title = _extract_title(data)
        if not title:
            return None

        is_dub = (type_.lower() == 'dub')

        # 1. Try mapped URLs first
        result = await _try_mapped_urls(anilist_id, ep, title, is_dub, provider_override)
        if result:
            return result

        # 2. Fallback to search
        return await _try_search_fallback(data, ep, title, is_dub, provider_override)
    except Exception as e:
        logger.error(f"Unexpected error in resolve_stream_with_anime_downloader: {e}")
        return None


def _extract_title(data: Dict[str, Any]) -> Optional[str]:
    title_obj = data.get('title', {})
    return title_obj.get('english') or title_obj.get('romaji') or title_obj.get('native')


async def _try_mapped_urls(anilist_id: int, ep: int, title: str, is_dub: bool, provider_override: Optional[str]) -> Optional[Dict[str, Any]]:
    candidates = await _get_mapped_candidates(anilist_id, is_dub, provider_override)
    result = await _resolve_via_mapped_urls(candidates, ep, title)
    if result:
        logger.info(f"Resolved direct stream via mapped {result['provider']} for id={anilist_id} ep={ep}")
        return result
    return None


async def _try_search_fallback(data: Dict[str, Any], ep: int, title: str, is_dub: bool, provider_override: Optional[str]) -> Optional[Dict[str, Any]]:
    queries = _build_search_queries(data, is_dub)
    providers = [provider_override] if provider_override else ['gogoanime', '9anime', 'animepahe', 'twistmoe']

    for provider in providers:
        result = await _search_provider(provider, queries, ep, title)
        if result:
            return result
    return None


async def _search_provider(provider: str, queries: list, ep: int, title: str) -> Optional[Dict[str, Any]]:
    try:
        cls = get_anime_class(provider)
        search_results = await _execute_queries(cls, queries)
        if not search_results:
            return None

        chosen_stub = _pick_best_stub(search_results, ep)
        anime_obj = chosen_stub.__class__(chosen_stub.url)
        episodes = getattr(anime_obj, 'episodes', [])
        target = _find_target_episode(episodes, ep)
        if not target:
            return None

        stream_url = getattr(target, 'stream_url', None)
        if not stream_url:
            return None

        return {
            "episode_info": {
                "title": getattr(target, 'pretty_title', f"{title}-{ep}"),
                "ep_no": getattr(target, 'ep_no', ep)
            },
            "provider": provider,
            "stream_links": [{"name": "direct", "url": stream_url}]
        }
    except Exception:
        return None


def _execute_queries(cls, queries: list) -> list:
    for q in queries:
        try:
            res = cls.search(q) or []
            if res:
                return res
        except Exception:
            continue
    return []


def _pick_best_stub(search_results: list, ep: int) -> Any:
    chosen_stub = None
    max_eps = -1
    for stub in search_results:
        try:
            obj = stub.__class__(stub.url)
            eps = getattr(obj, 'episodes', [])
            if eps:
                if len(eps) >= ep and chosen_stub is None:
                    return stub
                if len(eps) > max_eps:
                    max_eps = len(eps)
                    chosen_stub = stub
        except Exception:
            continue
    return chosen_stub or search_results[0]


def _find_target_episode(episodes: list, ep: int) -> Any:
    for e in episodes:
        eno = getattr(e, 'ep_no', None)
        if eno is not None and int(eno) == int(ep):
            return e
    if len(episodes) >= ep:
        return episodes[ep - 1]
    return None

