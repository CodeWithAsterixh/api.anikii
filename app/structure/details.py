import random

def structureAnilistDetails(dataObj: dict) -> dict:
    
    # Extract necessary fields with fallback/default values
    data = dataObj.get('data', {})
    
    anime_id_ext = dataObj.get('idSub', {}).get("id_provider",{})
    title = data['title'].get('english', data['title'].get('romaji', 'Unknown Title'))
    episodes = data.get('episodes', 0)  # Default 0 if not available
    status = data.get('status', 'UNKNOWN')
    cover_image = data['coverImage'].get('extraLarge', '')  # Default empty string
    banner_image = data.get('bannerImage', '')  # Default empty string
    
    # Cover Image: Use color if available, or generate a random color
    cover_image_color = data['coverImage'].get('color', f"#{random.randint(0, 0xFFFFFF):06x}")
    
    # Format: Use provided format or default to 'TV'
    format_type = data.get('format', 'TV')
    
    # Additional fields
    popularity = data.get('popularity', 0)
    average_score = data.get('averageScore', 0)
    trending = data.get('trending', 0)

    # Release Date
    release_date = data.get('startDate', {}).get('year', 'Unknown')
    season = data.get('FALL', None)
    seasonYear = data.get('seasonYear', 0)
    status = data.get('status', "FINISHED")
    type = data.get('type', None)
    trailer = data.get('trailer', {})
    nextAiringEpisode = data.get('nextAiringEpisode', {})
    tags = data.get('tags', [])
    
    

    # Create the structured object
    structured_data = {
        'id': data['id'],
        "anime_id_ext": anime_id_ext,
        'title': title,
        'episodes': episodes,
        'status': status,
        'coverImage': {
            "cover_image_color": cover_image_color,
            "cover_image": cover_image,
            "bannerImage": banner_image
        },
        'format': format_type,
        'popularity': popularity,
        'averageScore': average_score,
        'trending': trending,
        'releaseDate': release_date,
        'season': season,
        'seasonYear': seasonYear,
        'type': type,
        'trailer': trailer,
        'nextAiringEpisode': nextAiringEpisode,
        'tags': tags,
        
    }

    # Add structured object to the list

    return structured_data


def structureAnilistTrailer(data: dict) -> dict:
    
    # Extract necessary fields with fallback/default values

    trailer = data.get('trailer', {})

    # Create the structured object
    structured_data = {
        'trailer': trailer,
    }

    # Add structured object to the list

    return structured_data

# def structureAnilistCharacters(data: dict) -> dict:
    
#     # Extract necessary fields with fallback/default values

#     trailer = data.get('trailer', {})

#     # Create the structured object
#     structured_data = {
#         'trailer': trailer,
#     }

#     # Add structured object to the list

#     return structured_data
