from app.structure.listItem import structureAnilistItem, structureAnilistArray


def test_structure_item_defaults():
    input_data = {
        "id": 123,
        "title": {"romaji": "Romaji Title"},
        "coverImage": {"extraLarge": "http://image.example/test.jpg"},
        # Optional fields omitted to trigger defaults
    }
    result = structureAnilistItem(input_data)
    assert result["id"] == 123
    assert result["title"] == "Romaji Title"
    assert result["episodes"] == 0
    assert result["status"] == "UNKNOWN"
    assert "coverImage" in result
    assert result["coverImage"]["cover_image"] == "http://image.example/test.jpg"
    assert result["format"] == "TV"
    assert result["popularity"] == 0
    assert result["averageScore"] == 0
    assert result["trending"] == 0
    assert result["releaseDate"] == "Unknown"


def test_structure_array_wraps_items():
    input_list = [
        {
            "id": 456,
            "title": {"english": "English Title"},
            "coverImage": {"extraLarge": "http://image.example/cover.jpg"},
            "episodes": 12,
            "status": "FINISHED",
            "format": "TV",
            "popularity": 100,
            "averageScore": 80,
            "trending": 5,
            "startDate": {"year": 2020},
        }
    ]
    structured = structureAnilistArray(input_list)
    assert isinstance(structured, list)
    assert len(structured) == 1
    item = structured[0]
    assert item["id"] == 456
    assert item["title"] == "English Title"
    assert item["episodes"] == 12
    assert item["status"] == "FINISHED"
    assert item["format"] == "TV"
    assert item["releaseDate"] == 2020