from .collection import get_collection


async def delete_from_db(fileName: str) -> None:
    """Delete a single document by name from the database."""
    collection = get_collection()
    await collection.delete_one({"name": fileName})


# Backward-compatible alias for existing code that might still call DeleteDb
# Remove after all imports/usages are updated

async def DeleteDb(fileName: str) -> None:  # noqa: N802 (keep legacy name)
    await delete_from_db(fileName)
    
    


    