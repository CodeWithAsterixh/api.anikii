from .collection import get_collection


async def delete_from_db(file_name: str) -> None:
    """Delete a single document by name from the database."""
    collection = get_collection()
    await collection.delete_one({"name": file_name})


# Backward-compatible alias for existing code that might still call delete_db
# Remove after all imports/usages are updated

async def delete_db(file_name: str) -> None:  # noqa: N802 (keep legacy name)
    await delete_from_db(file_name)
    
    


    