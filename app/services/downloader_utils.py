import re
from typing import Dict, Any, List
from app.helpers.base import slugify_anikii

def sanitize_query(q: str) -> str:
    """Remove unwanted characters and normalize spaces for search queries."""
    # remove content inside parentheses and brackets
    q = re.sub(r"\([^)]*\)", "", q)
    q = re.sub(r"\[[^]]*\]", "", q)
    # remove punctuation except spaces and hyphens
    q = re.sub(r"[^\w\s-]", "", q)
    # normalize spaces
    q = re.sub(r"\s+", " ", q).strip()
    return q

def build_search_queries(data: Dict[str, Any], is_dub: bool) -> List[str]:
    """Build a list of search query variants based on anime metadata."""
    title_obj = data.get('title', {})
    title = title_obj.get('english') or title_obj.get('romaji') or title_obj.get('native')
    synonyms_list = data.get('synonyms', []) or []

    queries = _build_slug_queries(title_obj)
    queries = _add_base_and_sanitized(queries, title, synonyms_list)
    queries = _add_season_forms(queries, title)
    if is_dub:
        queries = _add_dub_variants(queries)

    return queries


def _build_slug_queries(title_obj: Dict[str, Any]) -> List[str]:
    eng = title_obj.get('english') or ''
    rom = title_obj.get('romaji') or ''
    anikii_id_eng = slugify_anikii(eng) if eng else None
    anikii_id_rom = slugify_anikii(rom) if rom else None
    return [q for q in [anikii_id_eng, anikii_id_rom] if q]


def _add_base_and_sanitized(queries: List[str], title: str, synonyms_list: List[str]) -> List[str]:
    base_queries = [title] + synonyms_list
    for bq in base_queries:
        if bq not in queries:
            queries.append(bq)
        sq = sanitize_query(bq)
        if sq and sq not in queries:
            queries.append(sq)
    return queries


def _add_season_forms(queries: List[str], title: str) -> List[str]:
    m = re.search(r"(Season|Cour|Part)\s*(\d)", title, flags=re.IGNORECASE)
    if not m:
        return queries
    num = m.group(2)
    base_title_sanitized = sanitize_query(title)
    queries.extend([
        f"{base_title_sanitized} {num}",
        f"{base_title_sanitized} S{num}",
        f"{base_title_sanitized} {num}nd",
        f"{base_title_sanitized} {num}th"
    ])
    return queries


def _add_dub_variants(queries: List[str]) -> List[str]:
    suffixes = [" dub", " (Dub)", " english dub", " [Dub]", " - Dub"]
    dub_queries = []
    for q in queries:
        dub_queries.append(q)
        for s in suffixes:
            dq = f"{q}{s}"
            if dq not in dub_queries:
                dub_queries.append(dq)
    return dub_queries

