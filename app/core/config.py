import os
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables once at import time
load_dotenv()


def _parse_allowed_origins(raw: Optional[str]) -> List[str]:
    """Parse a comma-separated list of origins into a clean list."""
    if raw:
        return [o.strip() for o in raw.split(",") if o and o.strip()]
    # Default allowed origins (can be overridden via ALLOWED_ORIGINS)
    return [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://anikii.vercel.app",
        "https://archive-anikii.vercel.app",
    ]


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        # MongoDB connection string (required)
        self.MONGO_URI: Optional[str] = os.getenv("MongoUri")
        # Database name (optional; defaults to 'anikii')
        self.DB_NAME: str = os.getenv("DB_NAME", "anikii")
        # CORS allowed origins as a list
        self.ALLOWED_ORIGINS: List[str] = _parse_allowed_origins(os.getenv("ALLOWED_ORIGINS"))


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get a singleton Settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings