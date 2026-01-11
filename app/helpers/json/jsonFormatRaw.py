import json
from datetime import datetime

def format_date(dt: datetime) -> str:
    """
    Format a datetime object to a string like:
    "Sat Feb  8 10:34:31 2025"
    Note: The day is right-aligned to mimic a two-character field.
    """
    # dt.strftime('%a %b %d %H:%M:%S %Y') produces a leading zero for single-digit days.
    # Instead, we'll manually format the day to avoid a leading zero.
    day_str = f"{dt.day:2d}"  # right-align in a 2-character field (space padded if necessary)
    # Combine parts: weekday, month, day, and the rest of the time and year.
    return dt.strftime("%a %b") + f" {day_str}" + dt.strftime(" %H:%M:%S %Y")

def generate_metadata(obj: any) -> dict:
    """
    Generates metadata for a JSON-parsed object.
    - file_size: based on the UTF-8 byte length of the JSON string (in MB, rounded to 2 decimals)
    - creation_time, modification_time, access_time: current time formatted as above.
    """
    # Convert the object to a JSON string.
    json_str = json.dumps(obj)
    # Compute the size in bytes (using UTF-8 encoding).
    size_in_bytes = len(json_str.encode('utf-8'))
    # Convert size to megabytes.
    size_in_mb = size_in_bytes / (1024)
    
    # Get the current datetime for all timestamps.
    now = datetime.now()
    formatted_time = format_date(now)
    
    return {
        "file_size": round(size_in_mb, 2),
        "creation_time": formatted_time,
        "modification_time": formatted_time,
        "access_time": formatted_time,
    }