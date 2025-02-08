import random
from app.helpers.formatAgeRange import format_range

def structureAnilistDetails(dataObj: dict) -> dict:
    
    # Extract necessary fields with fallback/default values
    data = dataObj.get('data', {})
    
    anime_id_ext = dataObj.get('idSub', {}).get("id_provider",{})
    title = data.get('title', {})
    synonyms = data.get('synonyms', [])
    episodes = data.get('episodes', 0)  # Default 0 if not available
    status = data.get('status', 'UNKNOWN')
    description = data.get('description', '')
    genres = data.get('genres', [])
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
    duration = data.get('duration', 0)

    # Release Date
    release_date = data.get('startDate', {}).get('year', 'Unknown')
    season = data.get('FALL', None)
    seasonYear = data.get('seasonYear', 0)
    status = data.get('status', "FINISHED")
    type = data.get('type', None)
    trailer = data.get('trailer', {})
    nextAiringEpisode = data.get('nextAiringEpisode', {})
    tags = data.get('tags', [])
    
    # studios
    studios = data.get('studios', {}).get("edges",None)
    
    # stats
    score_distribution = data.get('stats', {}).get("scoreDistribution",[])
    
    
    

    # Create the structured object
    structured_data = {
        'id': data['id'],
        "anime_id_ext": anime_id_ext,
        'title': title,
        "synonyms":synonyms,
        'description': description,
        "genres": genres,
        "studios":studios,
        'episodes': episodes,
        "duration":duration,
        'status': status,
        'coverImage': {
            "cover_image_color": cover_image_color,
            "cover_image": cover_image,
            "bannerImage": banner_image
        },
        'format': format_type,
        'popularity': popularity,
        'averageScore': average_score,
        "score_distribution":score_distribution,
        'trending': trending,
        'releaseDate': release_date,
        'season': {
            "type":season,
            'year': seasonYear,
        },
        'type': type,
        'trailer': trailer,
        'nextAiringEpisode': nextAiringEpisode,
        'tags': tags,
        
    }

    # Add structured object to the list

    return structured_data


def structureAnilistRelations(dataObj: dict) -> dict:
    
    # Extract necessary fields with fallback/default values
    data = dataObj.get('data', {})
    
    # relations
    relations = data.get("relations",{}).get("edges",[])
    relationsArray = []
    for relation in relations:
        relationObj = relation.get("node", {})
        relationsArray.append(relationObj)
    
    

    # Create the structured object
    structured_data = relationsArray

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

def structureAnilistCharacters(characters_list: list) -> list:
    
    # Extract necessary fields with fallback/default values
    results = []    
    for node in characters_list:
        character = node.get("node", {})
        characterId = character.get("id", None)
        name = character.get("name", {}).get("full", None)
        image = character.get("image", {}).get("large", None) or character.get("image", {}).get("medium", None)
        gender = character.get("gender", None)
        description = character.get("description", None)
        dateOfBirth = character.get("dateOfBirth", {})
        age = character.get("age", "")
        if age is not None:
          age = format_range(age)
        
        
        role = node.get("role", None)
        
        voiceActorsList = []
        
        voiceActors = node.get("voiceActors", {})
        
        for voiceActor in voiceActors:
            voiceActorsName = voiceActor.get("name", {}).get("full", None)
            voiceActorsLanguage = voiceActor.get("languageV2",None)
            voiceActorsImage = voiceActor.get("image", {}).get("large", None) or voiceActor.get("image", {}).get("medium", None)
            voiceActorsList.append({
                "name": voiceActorsName,
                "language": voiceActorsLanguage,
                "image": voiceActorsImage
            })
        
        results.append({
            "character":{
                "id": characterId,
                "role": role,
                "name": name,
                "image": image,
                "gender": gender,
                "description": description,
                "dateOfBirth": dateOfBirth,
                "age": age
            },
            "voiceActors":voiceActorsList
        })
        
        


   

    # Add structured object to the list

    return results
