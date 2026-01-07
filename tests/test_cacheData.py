import os
from typing import Dict, Any, List

from app.helpers.json._cache_data import run_cache_data, save_cache_data
from app.helpers.json.json_loader import jsonLoad
from app.helpers.json.clearTmp import delete_specific_file


TEST_FILE = "test__cache_data"


def cleanup_file():
    # Remove the temp file if it exists (using helper to match BASE_TMP_DIR)
    delete_specific_file(f"{TEST_FILE}.json")


def make_media_item(
    _id: int,
    title_en: str | None = None,
    title_romaji: str | None = None,
    extra_large: str | None = None,
    episodes: int | None = None,
    status: str | None = None,
    format_type: str | None = None,
    popularity: int | None = None,
    average_score: int | None = None,
    trending: int | None = None,
    start_year: int | None = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "id": _id,
        "title": {},
        "coverImage": {},
    }
    if title_en is not None:
        data["title"]["english"] = title_en
    if title_romaji is not None:
        data["title"]["romaji"] = title_romaji
    if extra_large is not None:
        data["coverImage"]["extraLarge"] = extra_large
    if episodes is not None:
        data["episodes"] = episodes
    if status is not None:
        data["status"] = status
    if format_type is not None:
        data["format"] = format_type
    if popularity is not None:
        data["popularity"] = popularity
    if average_score is not None:
        data["average_score"] = average_score
    if trending is not None:
        data["trending"] = trending
    if start_year is not None:
        data["startDate"] = {"year": start_year}
    return data


def test_run_cache_data_no_cache_returns_none():
    cleanup_file()
    assert run_cache_data(None, TEST_FILE) is None
    assert run_cache_data(1, TEST_FILE) is None


def test_save_cache_data_persists_and_caps_last_page():
    cleanup_file()
    media: List[Dict[str, Any]] = [
        make_media_item(
            _id=1,
            title_romaji="Romaji Title",
            extra_large="http://image.example/test.jpg",
        )
    ]
    page_info = {"lastPage": 123}

    saved = save_cache_data(page_info, media, TEST_FILE, page=2)
    assert saved["page_info"]["lastPage"] == 50
    assert saved["page_info"]["currentPage"] == 2
    assert isinstance(saved["data"], list)
    assert len(saved["data"]) == 1

    # Verify file content
    loaded = jsonLoad(TEST_FILE)
    assert loaded.get("lastPage") == 50
    assert "pages" in loaded
    assert "2" in loaded["pages"]
    assert isinstance(loaded["pages"]["2"], list)
    assert len(loaded["pages"]["2"]) == 1


def test_run_cache_data_returns_page_data():
    # Should use existing cache from previous test
    result = run_cache_data(2, TEST_FILE)
    assert result is not None
    assert result["page_info"]["lastPage"] == 50
    assert result["page_info"]["currentPage"] == 2
    assert isinstance(result["data"], list)
    assert len(result["data"]) == 1


def test_save_cache_data_appends_items_on_same_page():
    media2: List[Dict[str, Any]] = [
        make_media_item(
            _id=2,
            title_en="English Title",
            extra_large="http://image.example/cover2.jpg",
            episodes=12,
            status="FINISHED",
            format_type="TV",
            popularity=200,
            average_score=85,
            trending=10,
            start_year=2021,
        )
    ]
    page_info_2 = {"lastPage": 5}

    saved2 = save_cache_data(page_info_2, media2, TEST_FILE, page=2)
    assert saved2["page_info"]["lastPage"] == 5
    assert saved2["page_info"]["currentPage"] == 2

    # Verify the page now has 2 items
    loaded = jsonLoad(TEST_FILE)
    assert len(loaded["pages"]["2"]) == 2

    result = run_cache_data(2, TEST_FILE)
    assert result is not None
    assert len(result["data"]) == 2


def test_run_cache_data_page_not_exists_returns_none():
    assert run_cache_data(3, TEST_FILE) is None


def test_save_cache_data_structures_defaults():
    # Missing many optional fields; verify defaults
    media_default: List[Dict[str, Any]] = [
        make_media_item(
            _id=99,
            title_romaji="Default Romaji",
            extra_large="http://image.example/default.jpg",
            # No episodes/status/format/popularity/average_score/trending/startDate provided
        )
    ]
    page_info = {"lastPage": 1}
    saved = save_cache_data(page_info, media_default, TEST_FILE, page=1)
    assert saved["page_info"]["lastPage"] == 1
    assert saved["page_info"]["currentPage"] == 1
    assert len(saved["data"]) == 1

    item = saved["data"][0]
    assert item["id"] == 99
    assert item["title"] == "Default Romaji"
    assert item["episodes"] == 0
    assert item["status"] == "UNKNOWN"
    assert item["format"] == "TV"
    assert item["popularity"] == 0
    assert item["average_score"] == 0
    assert item["trending"] == 0
    assert item["releaseDate"] == "Unknown"

    # Clean up at end of test suite
    cleanup_file()