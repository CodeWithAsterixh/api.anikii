BASEURL="https://www14.gogoanimes.fi"

def slugify_anikii(name: str) -> str:
    """Convert a title to a lowercase hyphenated id suitable for providers.
    Example: "Blue Box" -> "blue-box"; strips non-alphanumerics except spaces and hyphens.
    """
    if not name:
        return ""
    import re
    # Normalize whitespace
    s = re.sub(r"\s+", " ", name).strip()
    # Remove parentheses/brackets content and punctuation except spaces/hyphens
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"\[[^]]*\]", "", s)
    s = re.sub(r"[^\w\s-]", "", s)
    # Lowercase and replace spaces with hyphens
    s = s.lower().strip()
    s = re.sub(r"\s+", "-", s)
    # Collapse multiple hyphens
    s = re.sub(r"-+", "-", s)
    return s

def substring_after(string: str, to_find: str) -> str:
    """Returns the part of the string after the first occurrence of to_find."""
    index = string.find(to_find)
    return "" if index == -1 else string[index + len(to_find):]

def substring_before(string: str, to_find: str) -> str:
    """Returns the part of the string before the first occurrence of to_find."""
    index = string.find(to_find)
    return "" if index == -1 else string[:index]