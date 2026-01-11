from .get import get_database

def get_collection(name: str = "listings"):
    """Get a motor collection handle."""
    db = get_database()
    return db.get_collection(name)