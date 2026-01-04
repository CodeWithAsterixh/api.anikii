from app.helpers.formatAgeRange import format_range

def structureAnilistCharacters(characters_list: list) -> list:
    results = []    
    for node in characters_list:
        character = node.get("node", {})
        characterId = character.get("id")
        name = character.get("name", {}).get("full")
        image = character.get("image", {}).get("large") or character.get("image", {}).get("medium")
        gender = character.get("gender")
        description = character.get("description")
        dateOfBirth = character.get("dateOfBirth", {})
        age = character.get("age", "")
        if age:
            age = format_range(age)
        
        role = node.get("role")
        voiceActorsList = []
        voiceActors = node.get("voiceActors", [])
        
        for voiceActor in voiceActors:
            vaName = voiceActor.get("name", {}).get("full")
            vaLang = voiceActor.get("languageV2")
            vaImage = voiceActor.get("image", {}).get("large") or voiceActor.get("image", {}).get("medium")
            voiceActorsList.append({
                "name": vaName,
                "language": vaLang,
                "image": vaImage
            })
        
        results.append({
            "character": {
                "id": characterId,
                "role": role,
                "name": name,
                "image": image,
                "gender": gender,
                "description": description,
                "dateOfBirth": dateOfBirth,
                "age": age
            },
            "voiceActors": voiceActorsList
        })
    return results
