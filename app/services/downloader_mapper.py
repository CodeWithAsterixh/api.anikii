import logging
from typing import Optional, List, Dict, Any
from anime_downloader.sites import get_anime_class
from app.helpers.modules import fetch_malsyn_data_and_get_provider

logger = logging.getLogger(__name__)

async def _get_mapped_candidates(anilist_id: int, is_dub: bool, provider_override: Optional[str] = None) -> List[Dict[str, str]]:
    """Get direct provider URL candidates from MalSync mapping."""
    try:
        malsync_map = await fetch_malsyn_data_and_get_provider(anilist_id)
        id_provider = (malsync_map or {}).get('id_provider') or {}
    except Exception as e:
        logger.debug(f"MalSync mapping fetch error: {e}")
        id_provider = {}

    candidates = []
    provider_order = [provider_override] if provider_override else ['gogoanime', 'animepahe', '9anime', 'twistmoe']
    
    for prov in provider_order:
        try:
            if prov == 'gogoanime':
                slug = id_provider.get('idGogoDub') if is_dub and id_provider.get('idGogoDub') else id_provider.get('idGogo')
                if slug:
                    for base in ['https://gogoanime.lu', 'https://gogoanime.app']:
                        candidates.append({'provider': 'gogoanime', 'url': f"{base}/category/{slug}"})
            elif prov == 'animepahe':
                pahe_id = id_provider.get('idPahe')
                if pahe_id:
                    candidates.append({'provider': 'animepahe', 'url': f"https://animepahe.com/anime/{pahe_id}"})
        except Exception:
            continue
    return candidates

async def _resolve_via_mapped_urls(candidates: List[Dict[str, str]], ep: int, title: str) -> Optional[Dict[str, Any]]:
    """Try to resolve stream directly using mapped URLs."""
    for cand in candidates:
        try:
            cls = get_anime_class(cand['provider'])
            anime_obj = cls(cand['url'])
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
                'episode_info': {
                    'title': getattr(target, 'pretty_title', f"{title}-{ep}"),
                    'ep_no': getattr(target, 'ep_no', ep)
                },
                'provider': cand['provider'],
                'stream_links': [{'name': 'direct', 'url': stream_url}]
            }
        except Exception as e:
            logger.debug(f"Error resolving via mapped URL {cand}: {e}")
            continue
    return None
