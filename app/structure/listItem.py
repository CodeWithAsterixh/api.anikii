import random



def structure_anilist_item(data:dict)->dict:
        anime_id = data.get('id')
        title_data = data.get('title') or {}
        title = title_data.get('english') or title_data.get('romaji') or 'Unknown Title'
        episodes = data.get('episodes')
        episodes = episodes if isinstance(episodes, int) else 0  # Default 0 if not available or None
        status = data.get('status') or 'UNKNOWN'
        cover_image_obj = data.get('coverImage') or {}
        cover_image = cover_image_obj.get('extraLarge') or ''  # Default empty string
        banner_image = data.get('bannerImage') or ''  # Default empty string
        
        # Cover Image: Use color if available, or generate a random color
        color_val = cover_image_obj.get('color')
        cover_image_color = color_val if isinstance(color_val, str) and color_val else f"#{random.randint(0, 0xFFFFFF):06x}"
        
        # Format: Use provided format or default to 'TV'
        format_type = data.get('format') or 'TV'
        
        # Additional fields
        popularity = data.get('popularity') or 0
        average_score = data.get('averageScore') or 0
        trending = data.get('trending') or 0

        # Release Date
        start_date = data.get('startDate') or {}
        release_year = start_date.get('year')
        release_date = release_year if isinstance(release_year, int) else 'Unknown'

        # Create the structured object
        structured_data = {
            'id': anime_id,
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
            'releaseDate': release_date
        }
        
        return structured_data
def structure_anilist_array(data_list: list) -> list:
    structured_list = []

    for data in data_list:
        # Extract necessary fields with fallback/default values
        structured_data = structure_anilist_item(data)

        # Add structured object to the list
        structured_list.append(structured_data)

    return structured_list
