import logging
from typing import Optional, List, Dict, Any
from anime_downloader.sites import get_anime_class
from app.helpers.modules import fetch_malsyn_data_and_get_provider

logger = logging.getLogger(__name__)

async def _get_id_provider(anilist_id: int) -> Dict[str, Any]:
    """Fetch MalSync mapping and return provider IDs."""
    try:
        malsync_map = await fetch_malsyn_data_and_get_provider(anilist_id)
        return (malsync_map or {}).get('id_provider') or {}
    except Exception as e:
        logger.debug(f"MalSync mapping fetch error: {e}")
        return {}


def _add_gogoanime_candidates(id_provider: Dict[str, Any], is_dub: bool, candidates: List[Dict[str, str]]):
    """Add GogoAnime candidates based on slug."""
    slug = id_provider.get('idGogoDub') if is_dub and id_provider.get('idGogoDub') else id_provider.get('idGogo')
    if slug:
        for base in ['https://gogoanime.lu', 'https://gogoanime.app']:
            candidates.append({'provider': 'gogoanime', 'url': f"{base}/category/{slug}"})


def _add_animepahe_candidates(id_provider: Dict[str, Any], candidates: List[Dict[str, str]]):
    """Add AnimePahe candidate based on ID."""
    pahe_id = id_provider.get('idPahe')
    if pahe_id:
        candidates.append({'provider': 'animepahe', 'url': f"https://animepahe.com/anime/{pahe_id}"})


async def get_mapped_candidates(anilist_id: int, is_dub: bool, provider_override: Optional[str] = None) -> List[Dict[str, str]]:
    """Get direct provider URL candidates from MalSync mapping."""
    id_provider = await _get_id_provider(anilist_id)
    candidates = []
    provider_order = [provider_override] if provider_override else ['gogoanime', 'animepahe', '9anime', 'twistmoe']
    
    for prov in provider_order:
        try:
            if prov == 'gogoanime':
                _add_gogoanime_candidates(id_provider, is_dub, candidates)
            elif prov == 'animepahe':
                _add_animepahe_candidates(id_provider, candidates)
        except Exception:
            continue
    return candidates

def _find_target_episode(episodes, ep):
    """Find the target episode object from a list of episodes."""
    for e in episodes:
        eno = getattr(e, 'ep_no', None)
        if eno is not None and int(eno) == int(ep):
            return e
    if len(episodes) >= ep:
        return episodes[ep - 1]
    return None


def _build_result(target, provider, title, ep):
    """Build the result dictionary for a resolved stream."""
    stream_url = getattr(target, 'stream_url', None)
    if not stream_url:
        return None
    return {
        'episode_info': {
            'title': getattr(target, 'pretty_title', f"{title}-{ep}"),
            'ep_no': getattr(target, 'ep_no', ep)
        },
        'provider': provider,
        'stream_links': [{'name': 'direct', 'url': stream_url}]
    }


def _try_candidate(cand, ep, title):
    """Attempt to resolve a stream from a single candidate."""
    try:
        cls = get_anime_class(cand['provider'])
        anime_obj = cls(cand['url'])
        episodes = getattr(anime_obj, 'episodes', [])
        if not episodes:
            return None
        target = _find_target_episode(episodes, ep)
        if not target:
            return None
        return _build_result(target, cand['provider'], title, ep)
    except Exception as e:
        logger.debug(f"Error resolving via mapped URL {cand}: {e}")
        return None


def resolve_via_mapped_urls(candidates: List[Dict[str, str]], ep: int, title: str) -> Optional[Dict[str, Any]]:
    """Try to resolve stream directly using mapped URLs."""
    for cand in candidates:
        result = _try_candidate(cand, ep, title)
        if result:
            return result
    return None
