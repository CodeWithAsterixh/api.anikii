import os

def get_files_with_prefix(directory="/tmp/anikii", prefix=""):
    """
    Returns a list of files and folders in the given directory that contain the specified prefix.
    """
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return []

    # Filter files that contain the prefix
    matching_files = [f for f in os.listdir(directory) if prefix in f]

    return matching_files


