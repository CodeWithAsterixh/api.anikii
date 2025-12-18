from .collection import collection_name


def delete_from_db(fileName: str) -> None:
    """Delete a single document by name from the database."""
    collection_name.find_one_and_delete({"name": fileName})


# Backward-compatible alias for existing code that might still call DeleteDb
# Remove after all imports/usages are updated

def DeleteDb(fileName: str) -> None:  # noqa: N802 (keep legacy name)
    delete_from_db(fileName)
    
    


    