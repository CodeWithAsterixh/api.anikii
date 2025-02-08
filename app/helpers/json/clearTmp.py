import os
import shutil

def clear_anikii_route(directory="/tmp/anikii", prefix="", filename_td=""):
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


def delete_specific_file( filename="",directory="/tmp/anikii"):
    """
    Deletes a specific file in the given directory.
    Returns True if the file was deleted, False otherwise.
    """
    file_path = os.path.join(directory, filename)

    if not os.path.exists(file_path):
        print(f"File '{file_path}' does not exist.")
        return False

    try:
        os.unlink(file_path)  # Remove the file
        print(f"Deleted: {file_path}")
        return True
    except Exception as e:
        print(f"Failed to delete {file_path}: {e}")
        return False
