from fastapi import FastAPI # type: ignore
from app.routes import (
    anime_ID_stream_EP_extra,
    home,
    popular,
    popular_upcoming,
    popular_releases,
    popular_releases_seasons,
    popular_releases_seasons_SEASON,
    popular_releases_seasons_SEASON_YEAR,
    search,
    genres,
    genres_GENRE,
    fyp,
    anime_ID,
    anime_ID_relations,
    anime_ID_characters,
    anime_ID_recommended,
    anime_ID_stream,
    anime_ID_stream_EP,
    anime_ID_stream_EP_dub,
    anime_ID_trailers,
    anime_ID_stream_external,
    clearTmp,
    listTmp,
    clear_specific_tmp_file,
    select_specific_tmp_file,
)

# Initialize the FastAPI application
app = FastAPI()

# Route configurations
routes = [
    home.router,
    popular.router,
    popular_releases.router,
    popular_releases_seasons.router,
    popular_releases_seasons_SEASON.router,
    popular_releases_seasons_SEASON_YEAR.router,
    search.router,
    genres.router,
    genres_GENRE.router,
    fyp.router,
    anime_ID.router,
    anime_ID_relations.router,
    anime_ID_characters.router,
    anime_ID_recommended.router,
    anime_ID_stream.router,
    anime_ID_stream_EP.router,
    anime_ID_stream_EP_dub.router,
    anime_ID_stream_EP_extra.router,
    anime_ID_trailers.router,
    popular_upcoming.router,
    anime_ID_stream_external.router,
    clearTmp.router,
    listTmp.router,
    clear_specific_tmp_file.router,
    select_specific_tmp_file.router,
]

# Include all routes in the application
for route in routes:
    app.include_router(route)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "API is up and running! go to /popular"}
