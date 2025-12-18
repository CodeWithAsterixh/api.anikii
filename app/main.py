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
from app.core.config import get_settings



#load environment
load_dotenv()

# Initialize the FastAPI application
app = FastAPI()

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Global exception handlers using standardized envelope
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.helpers.response_envelope import error_response, success_response

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    body = error_response(
        request,
        status_code=exc.status_code,
        message=str(exc.detail) if exc.detail is not None else "HTTP error",
        error={"type": "HTTPException"}
    )
    return JSONResponse(status_code=exc.status_code, content=body)

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    body = error_response(
        request,
        status_code=500,
        message="Server error",
        error={"type": exc.__class__.__name__, "detail": str(exc)}
    )
    return JSONResponse(status_code=500, content=body)

# Health check endpoint
@app.get("/health")
def health_check(request: Request):
    return success_response(request, data={"status": "API is up and running! go to /popular"})
