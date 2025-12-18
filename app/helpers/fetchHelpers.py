# config.py
BASE_URL_ANILIST = "https://graphql.anilist.co"

# request_options.py
import json
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


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


def _create_session() -> requests.Session:
    """Create a configured requests Session with retry/backoff for transient errors."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=frozenset(["POST", "GET"]),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


# Module-level session for connection reuse and retries
SESSION = _create_session()


def make_api_request(body_obj: dict, timeout: float = 10.0) -> dict:
    """
    Send a POST request to Anilist GraphQL endpoint and return the JSON response.
    Raises requests.exceptions.RequestException on network or HTTP errors.
    Includes retry/backoff via a configured Session for resilience.
    """
    options = get_options(body_obj)
    response = SESSION.post(
        BASE_URL_ANILIST,
        headers=options['headers'],
        data=options['body'],
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()
