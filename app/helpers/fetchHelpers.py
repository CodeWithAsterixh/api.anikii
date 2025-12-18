# config.py
BASE_URL_ANILIST = "https://graphql.anilist.co"

# request_options.py
import json
import httpx
import asyncio
import random
from typing import Optional


def get_options(body_obj: dict) -> dict:
    """Return the headers and body for making a POST request."""
    return {
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "anikii-api/1.0 (+https://github.com/asterixh/anikii)",
            "Accept-Encoding": "gzip, deflate, br",
        },
        # Keep Python dict for json parameter; requests will serialize efficiently
        "body": body_obj,
    }


# Async HTTP client (module-level) for connection reuse
_async_client: Optional[httpx.AsyncClient] = None

async def _get_async_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None:
        timeout = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
        _async_client = httpx.AsyncClient(timeout=timeout, limits=limits, follow_redirects=True, headers={
            "User-Agent": "anikii-api/1.0 (+https://github.com/asterixh/anikii)",
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
        })
    return _async_client

async def make_api_request_async(body_obj: dict, timeout: float = 10.0, max_retries: int = 3, backoff_factor: float = 0.3) -> dict:
    """
    Async POST to Anilist GraphQL using httpx.AsyncClient with connection pooling.
    Implements retry with exponential backoff and jitter for transient errors (429/5xx).
    Returns parsed JSON; raises httpx.HTTPError on network/HTTP errors.
    """
    client = await _get_async_client()
    attempt = 0
    statuses = {429, 500, 502, 503, 504}
    last_exc = None
    while attempt <= max_retries:
        try:
            resp = await client.post(BASE_URL_ANILIST, json=body_obj, timeout=timeout)
            if resp.status_code in statuses and attempt < max_retries:
                delay = backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)
                attempt += 1
                continue
            resp.raise_for_status()
            return resp.json()
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            last_exc = e
            if attempt < max_retries:
                delay = backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)
                attempt += 1
                continue
            raise
    if last_exc:
        raise last_exc

# Optional: graceful closing at shutdown (call in app startup/shutdown events)
async def close_async_client():
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None
