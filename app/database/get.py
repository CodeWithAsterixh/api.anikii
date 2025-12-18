from pymongo import MongoClient
from app.core.config import get_settings


def get_database():
    """
    Initialize and return a MongoDB database handle using the configured connection string.

    Reads the MongoDB URI and database name from environment variables via app.core.config.
    Raises a RuntimeError if the MongoDB URI is not provided.
    """
    settings = get_settings()
    uri = settings.MONGO_URI
    if not uri:
        raise RuntimeError(
            "MongoUri environment variable is missing. Set it in your .env file and avoid committing secrets to source control."
        )

    client = MongoClient(uri)
    return client.get_database(settings.DB_NAME)
    
    

