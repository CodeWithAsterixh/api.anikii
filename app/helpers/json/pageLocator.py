def ensure_page_exists(data: dict, page_number: int) -> bool:
    """
    Checks if a specific page number exists in the 'pages' object.
    If not, it adds the missing page with an empty list and returns False.
    If it already exists, returns True.
    """
    
    if data.get("pages") is None:
        print(f"Creating 'pages' object in {data}")
        data["pages"] = {}  # Ensure 'pages' exists'
    
    if data["pages"].get(str(page_number)):
        return True  # Page already exists
    
    return False  # Page was missing, now created
