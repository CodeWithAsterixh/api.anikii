import os
import tempfile

BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")


def get_files_with_prefix(directory: str | None = None, prefix: str = ""):
    """
    Returns a list of files and folders in the given directory that contain the specified prefix.
    Defaults to the cross-platform temp directory.
    """
    directory = directory or BASE_TMP_DIR

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return []

    # Filter files that contain the prefix
    matching_files = [f for f in os.listdir(directory) if prefix in f]

    return matching_files


