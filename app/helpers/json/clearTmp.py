import os
import shutil

def clear_anikii_route(directory="/tmp/anikii", prefix=""):
    """
    Deletes all files and folders in the given directory that start with the given prefix.
    Returns a list of deleted items.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return []

    deleted_files = []  # Store deleted filenames

    for filename in os.listdir(directory):
        if filename.startswith(prefix):  # Check if filename starts with "anikiiRoute"
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
