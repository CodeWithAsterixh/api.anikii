from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from starlette.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from secure import Secure

from app.core.limiter import limiter
from app.routes import (
    home,
    popular,
    search,
    genres,
    fyp,
    anime,
    stream_metadata,
    stream_actions,
    admin
)
from app.core.config import get_settings
from app.helpers.fetchHelpers import close_async_client, _get_async_client
from app.database.get import get_database, close_database



from app.core.exceptions import register_exception_handlers
from app.helpers.response_envelope import success_response

# load environment
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize shared AsyncClient and Database
    await _get_async_client()
    get_database() # Ensure DB client is initialized
    yield
    # Shutdown: Gracefully close shared AsyncClient and Database
    await close_async_client()
    close_database()

# Initialize FastAPI app with lifespan
app = FastAPI(default_response_class=ORJSONResponse, lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register global exception handlers
register_exception_handlers(app)

# Initialize Secure headers
secure_headers = Secure.with_default_headers()

@app.middleware("http")
async def set_secure_headers(request: Request, call_next):
    response = await call_next(request)
    secure_headers.set_headers(response)
    # Additional security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; object-src 'none';"
    return response

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=512)

# Route configurations
routes = [
    home.router,
    popular.router,
    search.router,
    genres.router,
    fyp.router,
    anime.router,
    stream_metadata.router,
    stream_actions.router,
    admin.router,
]


# Include all routes in the application
for route in routes:
    app.include_router(route)

# Health check endpoint
@app.get("/health")
def health_check(request: Request):
    return success_response(request, data={"status": "API is up and running! go to /popular"})
