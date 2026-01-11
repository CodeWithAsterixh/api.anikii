from app.helpers.formatAgeRange import format_range

def structure_anilist_characters(characters_list: list) -> list:
    results = []    
    for node in characters_list:
        character = node.get("node", {})
        character_id = character.get("id")
        name = character.get("name", {}).get("full")
        image = character.get("image", {}).get("large") or character.get("image", {}).get("medium")
        gender = character.get("gender")
        description = character.get("description")
        date_of_birth = character.get("dateOfBirth", {})
        age = character.get("age", "")
        if age:
            age = format_range(age)
        
        role = node.get("role")
        voice_actors_list = []
        voice_actors = node.get("voiceActors", [])
        
        for voice_actor in voice_actors:
            va_name = voice_actor.get("name", {}).get("full")
            va_lang = voice_actor.get("languageV2")
            va_image = voice_actor.get("image", {}).get("large") or voice_actor.get("image", {}).get("medium")
            voice_actors_list.append({
                "name": va_name,
                "language": va_lang,
                "image": va_image
            })
        
        results.append({
            "character": {
                "id": character_id,
                "role": role,
                "name": name,
                "image": image,
                "gender": gender,
                "description": description,
                "date_of_birth": date_of_birth,
                "age": age
            },
            "voice_actors": voice_actors_list
        })
    return results
