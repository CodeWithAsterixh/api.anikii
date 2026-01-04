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
        title_obj = data.get('title', {})
        title = title_obj.get('english') or title_obj.get('romaji') or title_obj.get('native')
        if not title:
            return None

        is_dub = (type_.lower() == 'dub')
        
        # 1. Try mapped URLs first
        candidates = await _get_mapped_candidates(anilist_id, is_dub, provider_override)
        result = await _resolve_via_mapped_urls(candidates, ep, title)
        if result:
            logger.info(f"Resolved direct stream via mapped {result['provider']} for id={anilist_id} ep={ep}")
            return result

        # 2. Fallback to search
        queries = _build_search_queries(data, is_dub)
        providers = [provider_override] if provider_override else ['gogoanime', '9anime', 'animepahe', 'twistmoe']
        
        for provider in providers:
            try:
                cls = get_anime_class(provider)
                search_results = []
                for q in queries:
                    try:
                        res = cls.search(q) or []
                        if res:
                            search_results = res
                            break
                    except Exception:
                        continue
                
                if not search_results:
                    continue

                chosen_stub = None
                max_eps = -1
                for stub in search_results:
                    try:
                        obj = stub.__class__(stub.url)
                        eps = getattr(obj, 'episodes', [])
                        if eps:
                            if len(eps) >= ep and chosen_stub is None:
                                chosen_stub = stub
                                break
                            if len(eps) > max_eps:
                                max_eps = len(eps)
                                chosen_stub = stub
                    except Exception:
                        continue
                
                if not chosen_stub:
                    chosen_stub = search_results[0]
                
                anime_obj = chosen_stub.__class__(chosen_stub.url)
                episodes = getattr(anime_obj, 'episodes', [])
                if not episodes:
                    continue

                target = None
                for e in episodes:
                    eno = getattr(e, 'ep_no', None)
                    if eno is not None and int(eno) == int(ep):
                        target = e
                        break
                
                if target is None and len(episodes) >= ep:
                    target = episodes[ep - 1]
                
                if not target:
                    continue

                stream_url = getattr(target, 'stream_url', None)
                if not stream_url:
                    continue

                return {
                    "episode_info": {
                        "title": getattr(target, 'pretty_title', f"{title}-{ep}"),
                        "ep_no": getattr(target, 'ep_no', ep)
                    },
                    "provider": provider,
                    "stream_links": [{"name": "direct", "url": stream_url}]
                }
            except Exception:
                continue

        return None
    except Exception as e:
        logger.error(f"Unexpected error in resolve_stream_with_anime_downloader: {e}")
        return None
