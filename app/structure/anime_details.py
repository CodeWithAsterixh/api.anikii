import random
from app.helpers.base import slugify_anikii

def structure_anilist_details(data_obj: dict) -> dict:
    # Extract necessary fields with fallback/default values
    data = data_obj.get('data', {})
    
    anime_id_ext = data_obj.get('id_sub', {}).get("id_provider",{})
    title = data.get('title', {})
    synonyms = data.get('synonyms', [])
    episodes = data.get('episodes', 0)
    description = data.get('description', '')
    genres = data.get('genres', [])
    cover_image = data.get('coverImage', {}).get('extraLarge', '')
    banner_image = data.get('banner_image', '')
    
    english_title = title.get('english') or ''
    romaji_title = title.get('romaji') or ''
    anikii_id_eng = slugify_anikii(english_title) if english_title else None
    anikii_id_rom = slugify_anikii(romaji_title) if romaji_title else None
    anikii_ids = [v for v in [anikii_id_eng, anikii_id_rom] if v]
    
    cover_image_color = data.get('coverImage', {}).get('color', f"#{random.randint(0, 0xFFFFFF):06x}")
    format_type = data.get('format', 'TV')
    popularity = data.get('popularity', 0)
    average_score = data.get('averageScore', 0)
    trending = data.get('trending', 0)
    duration = data.get('duration', 0)
    release_date = data.get('startDate', {}).get('year', 'Unknown')
    season = data.get('FALL', None)
    season_year = data.get('season_year', 0)
    status = data.get('status', "FINISHED")
    type_ = data.get('type', None)
    trailer = data.get('trailer', {})
    next_airing_episode = data.get('nextAiringEpisode', {})
    tags = data.get('tags', [])
    
    studios = data.get('studios', {}).get("edges",[])
    studios_list = [node.get("node", {}).get("name") for node in studios if node.get("node", {}).get("name")]
    
    score_distribution = data.get('stats', {}).get("scoreDistribution",[])
    
    return {
        'id': data.get('id'),
        "anime_id_ext": anime_id_ext,
        'title': title,
        "anikii_id_eng": anikii_id_eng,
        "anikii_id_rom": anikii_id_rom,
        "anikii_ids": anikii_ids,
        "synonyms": synonyms,
        'description': description,
        "genres": genres,
        "studios": studios_list,
        'episodes': episodes,
        "duration": duration,
        'status': status,
        'coverImage': {
            "cover_image_color": cover_image_color,
            "cover_image": cover_image,
            "banner_image": banner_image
        },
        'format': format_type,
        'popularity': popularity,
        'averageScore': average_score,
        "score_distribution": score_distribution,
        'trending': trending,
        'releaseDate': release_date,
        'season': {
            "type": season,
            'year': season_year,
        },
        'type': type_,
        'trailer': trailer,
        'next_airing_episode': next_airing_episode,
        'tags': tags,
    }

def structure_anilist_relations(data_obj: dict) -> list:
    data = data_obj.get('data', {})
    relations = data.get("relations", {}).get("edges", [])
    return [relation.get("node", {}) for relation in relations]

def structure_anilist_trailer(data: dict) -> dict:
    return {'trailer': data.get('trailer', {})}
