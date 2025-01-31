import random

def structureAnilistArray(data_list: list) -> list:
    structured_list = []

    for data in data_list:
        # Extract necessary fields with fallback/default values
        anime_id = data['id']
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

        # Add structured object to the list
        structured_list.append(structured_data)

    return structured_list
