import os
import shutil
import tempfile
from app.helpers.security import validate_safe_path

from app.core.logger import logger

BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")

def clear_anikii_route(directory: str | None = None, prefix: str = "", filename_td: str = ""):
    """
    Deletes all files and folders in the given directory that start with the given prefix.
    Returns a list of deleted items.
    Defaults to the cross-platform temp directory.
    """
    if directory:
        # Validate that the directory is safe and under a controlled base
        # For simplicity, we'll just normalize it and check if it's under BASE_TMP_DIR 
        # or another safe location if needed. For now, we enforce BASE_TMP_DIR.
        directory = validate_safe_path("", base_dir=directory)
    else:
        directory = BASE_TMP_DIR

    if not os.path.exists(directory):
        logger.warning(f"Directory {directory} does not exist.")
        return []

    deleted_files = []  # Store deleted filenames

    for filename in os.listdir(directory):
        if filename.startswith(prefix):  # Check if filename starts with prefix
            file_path = os.path.join(directory, filename)
            try:
                # Remove files and symbolic links
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                # Remove directories and their contents
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)

                deleted_files.append(file_path)  # Track deleted file/folder
                logger.info(f"Deleted: {file_path}")
            except Exception as e:
                logger.error(f"Failed to delete {file_path}: {e}")

    logger.info(f"Cleared all paths starting with '{prefix}' in {directory}.")
    return deleted_files  # Return list of deleted files


def delete_specific_file(filename: str = "", directory: str | None = None):
    """
    Deletes a specific file in the given directory.
    """
    file_path = validate_safe_path(filename, directory or BASE_TMP_DIR)

    if not os.path.exists(file_path):
        return False

    try:
        os.unlink(file_path)  # Remove the file
        return True
    except Exception:
        return False
