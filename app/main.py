from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

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
    clear_specific_tmp_file,
    select_specific_tmp_file,
    save_data,
    savedDatas
)



#load environment
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000","http://localhost:5173","https://anikii.vercel.app","https://archive-anikii.vercel.app"],  # Allow only frontend origin
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

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
    savedDatas.router,
    clear_specific_tmp_file.router,
    select_specific_tmp_file.router,
    save_data.router,
]


# Include all routes in the application
for route in routes:
    app.include_router(route)

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "API is up and running! go to /popular"}
