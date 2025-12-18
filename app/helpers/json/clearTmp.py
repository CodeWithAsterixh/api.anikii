import os
import shutil
import tempfile

BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")


def clear_anikii_route(directory: str | None = None, prefix: str = "", filename_td: str = ""):
    """
    Deletes all files and folders in the given directory that start with the given prefix.
    Returns a list of deleted items.
    Defaults to the cross-platform temp directory.
    """
    directory = directory or BASE_TMP_DIR

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
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
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Failed to delete {file_path}: {e}")

    print(f"Cleared all paths starting with '{prefix}' in {directory}.")
    return deleted_files  # Return list of deleted files


def delete_specific_file(filename: str = "", directory: str | None = None):
    """
    Deletes a specific file in the given directory.
    Returns True if the file was deleted, False otherwise.
    Defaults to the cross-platform temp directory.
    """
    directory = directory or BASE_TMP_DIR
    file_path = os.path.join(directory, filename)

    if not os.path.exists(file_path):
        return False

    try:
        os.unlink(file_path)  # Remove the file
        return True
    except Exception:
        return False
