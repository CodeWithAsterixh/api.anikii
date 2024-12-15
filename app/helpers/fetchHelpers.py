# config.py
BASE_URL_ANILIST = "https://graphql.anilist.co"

# request_options.py
import json
import requests

def get_options(body_obj: dict) -> dict:
    """Return the headers and body for making a POST request."""
    return {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        "body": json.dumps(body_obj),  # Convert the Python dictionary to JSON string
    }

def make_api_request(body_obj: dict) -> dict:
    """Send a POST request to Anilist GraphQL endpoint and return the response."""
    options = get_options(body_obj)
    response = requests.post(BASE_URL_ANILIST, headers=options['headers'], data=options['body'])
    return response.json()
