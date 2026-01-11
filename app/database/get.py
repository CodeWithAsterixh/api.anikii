from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import get_settings

# Module-level singleton client for connection reuse and pooling
_client: AsyncIOMotorClient | None = None

def get_database():
    """
    Initialize and return a MongoDB database handle using the configured connection string.

    Reads the MongoDB URI and database name from environment variables via app.core.config.
    Raises a RuntimeError if the MongoDB URI is not provided.
    """
    global _client
    settings = get_settings()
    uri = settings.MONGO_URI
    if not uri:
        raise RuntimeError(
            "MongoUri environment variable is missing. Set it in your .env file and avoid committing secrets to source control."
        )

    if _client is None:
        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
    return _client.get_database(settings.DB_NAME)

def close_database():
    """Close the MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None
    
    

