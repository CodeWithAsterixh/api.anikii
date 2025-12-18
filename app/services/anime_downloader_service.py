import logging
import re
from typing import Optional

from app.services.anilist_service import fetch_anime_details
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import slugify_anikii
from anime_downloader.sites import get_anime_class

logger = logging.getLogger(__name__)

async def resolve_stream_with_anime_downloader(anilist_id: int, ep: int, type_: str, provider_override: Optional[str] = None):
    """
    Resolve a stream for a given AniList ID and episode using anime-downloader providers.
    - Prefers direct provider URLs from MalSync mappings when available (e.g., Gogoanime/Animepahe)
    - Falls back to provider search with slug-first queries (English/Romaji) and sanitized variants
    - Handles dub query suffixes heuristically
    Returns a dict with episode_info, provider, and stream_links (direct) or None.
    """
    try:
        data = fetch_anime_details(anilist_id)
        title_obj = data.get('title', {})
        title = title_obj.get('english') or title_obj.get('romaji') or title_obj.get('native')
        if not title:
            return None

        # First, try using MalSync mapped provider URLs to avoid search mismatches
        try:
            malsync_map = await fetch_malsyn_data_and_get_provider(anilist_id)
            id_provider = (malsync_map or {}).get('id_provider') or {}
        except Exception as e:
            logger.debug(f"MalSync mapping fetch error: {e}")
            id_provider = {}
        is_dub = (type_.lower() == 'dub')
        # Build direct URLs from mapping when available
        mapped_candidates = []
        # Determine provider preference order
        provider_order = [provider_override] if provider_override else ['gogoanime', 'animepahe', '9anime', 'twistmoe']
        for prov in provider_order:
            try:
                if prov == 'gogoanime':
                    slug = id_provider.get('idGogoDub') if is_dub and id_provider.get('idGogoDub') else id_provider.get('idGogo')
                    if slug:
                        for base in ['https://gogoanime.lu', 'https://gogoanime.app']:
                            mapped_candidates.append({'provider': 'gogoanime', 'url': f"{base}/category/{slug}"})
                elif prov == 'animepahe':
                    pahe_id = id_provider.get('idPahe')
                    if pahe_id:
                        mapped_candidates.append({'provider': 'animepahe', 'url': f"https://animepahe.com/anime/{pahe_id}"})
                # 9anime and twistmoe are search-only here since MalSync mapping isn't extracted for them in modules.py
            except Exception:
                continue
        # Try mapped URLs first
        for cand in mapped_candidates:
            try:
                cls = get_anime_class(cand['provider'])
                anime_obj = cls(cand['url'])
                episodes = getattr(anime_obj, 'episodes', [])
                logger.debug(f"MalSync {cand['provider']} object has {len(episodes)} episodes for URL {cand['url']}")
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
                episode_info = {
                    'title': getattr(target, 'pretty_title', f"{title}-{ep}"),
                    'ep_no': getattr(target, 'ep_no', ep)
                }
                logger.info(f"Resolved direct stream via mapped {cand['provider']} for id={anilist_id} ep={ep}: {stream_url}")
                return {
                    'episode_info': episode_info,
                    'provider': cand['provider'],
                    'stream_links': [{'name': 'direct', 'url': stream_url}]
                }
            except Exception as e:
                logger.debug(f"Error resolving via mapped URL {cand}: {e}")
                continue

        def sanitize_query(q: str) -> str:
            # remove content inside parentheses and brackets
            q = re.sub(r"\([^)]*\)", "", q)
            q = re.sub(r"\[[^]]*\]", "", q)
            # remove punctuation except spaces and hyphens
            q = re.sub(r"[^\w\s-]", "", q)
            # normalize spaces
            q = re.sub(r"\s+", " ", q).strip()
            return q

        # Build candidate queries (handle dub heuristics across providers)
        synonyms_list = data.get('synonyms', []) or []
        base_queries = [title] + synonyms_list

        # Prefer slug-based queries derived from English/Romaji titles
        anikii_id_eng = None
        anikii_id_rom = None
        try:
            eng = title_obj.get('english') or ''
            rom = title_obj.get('romaji') or ''
            anikii_id_eng = slugify_anikii(eng) if eng else None
            anikii_id_rom = slugify_anikii(rom) if rom else None
        except Exception:
            pass
        preferred_queries = [q for q in [anikii_id_eng, anikii_id_rom] if q]

        # Add sanitized variants and common season forms
        season_forms = []
        m = re.search(r"(Season|Cour|Part)\s*(\d)", title, flags=re.IGNORECASE)
        if m:
            num = m.group(2)
            season_forms = [
                f"{sanitize_query(title)} {num}",
                f"{sanitize_query(title)} S{num}",
                f"{sanitize_query(title)} {num}nd",
                f"{sanitize_query(title)} {num}th"
            ]
        queries = preferred_queries.copy()
        for bq in base_queries:
            queries.append(bq)
            sq = sanitize_query(bq)
            if sq and sq != bq:
                queries.append(sq)
        queries.extend(season_forms)
        if is_dub:
            suffixes = [" dub", " (Dub)", " english dub", " [Dub]", " - Dub"]
            dub_queries = []
            for q in queries:
                dub_queries.append(q)
                for s in suffixes:
                    dq = f"{q}{s}"
                    if dq not in dub_queries:
                        dub_queries.append(dq)
            queries = dub_queries
        logger.debug(f"anime-downloader queries built (slug-first) for id={anilist_id}, ep={ep}, type={type_}: {queries[:5]}... total={len(queries)}")

        # Try multiple providers supported by anime-downloader
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
                            logger.debug(f"Provider {provider} matched query '{q}' with {len(res)} results")
                            break
                    except Exception as e:
                        logger.debug(f"Provider {provider} search error for query '{q}': {e}")
                        continue
                if not search_results:
                    logger.debug(f"Provider {provider} had no search results")
                    continue
                # Choose a result whose episode list covers requested ep, otherwise pick the one with max episodes
                chosen_stub = None
                max_eps = -1
                for stub in search_results:
                    try:
                        obj = stub.__class__(stub.url)
                        eps = getattr(obj, 'episodes', [])
                        if eps:
                            if len(eps) >= ep and chosen_stub is None:
                                chosen_stub = stub
                                logger.debug(f"Provider {provider} chose stub covering ep {ep}: {stub.url} with {len(eps)} eps")
                                break
                            if len(eps) > max_eps:
                                max_eps = len(eps)
                                chosen_stub = stub
                    except Exception as e:
                        logger.debug(f"Provider {provider} error creating object from stub {getattr(stub, 'url', '')}: {e}")
                        continue
                if not chosen_stub:
                    chosen_stub = search_results[0]
                anime_obj = chosen_stub.__class__(chosen_stub.url)
                episodes = getattr(anime_obj, 'episodes', [])
                logger.debug(f"Provider {provider} selected anime has {len(episodes)} episodes")
                if not episodes:
                    continue
                target = None
                # Prefer matching ep_no if available
                for e in episodes:
                    eno = getattr(e, 'ep_no', None)
                    if eno is not None and int(eno) == int(ep):
                        target = e
                        break
                # Fallback to index if ep_no matching failed
                if target is None and len(episodes) >= ep:
                    target = episodes[ep - 1]
                if not target:
                    logger.debug(f"Provider {provider} did not find target episode {ep}")
                    continue
                stream_url = getattr(target, 'stream_url', None)
                if not stream_url:
                    logger.debug(f"Provider {provider} target episode has no stream_url")
                    continue
                episode_info = {
                    "title": getattr(target, 'pretty_title', f"{title}-{ep}"),
                    "ep_no": getattr(target, 'ep_no', ep)
                }
                logger.info(f"Resolved direct stream via {provider} for id={anilist_id} ep={ep}: {stream_url}")
                return {
                    "episode_info": episode_info,
                    "provider": provider,
                    "stream_links": [{"name": "direct", "url": stream_url}]
                }
            except Exception as e:
                logger.debug(f"Provider {provider} resolution error: {e}")
                # Try next provider on failure
                continue
        logger.info(f"anime-downloader failed to resolve stream for id={anilist_id} ep={ep} type={type_} override={provider_override}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error in resolve_stream_with_anime_downloader: {e}")
        return None