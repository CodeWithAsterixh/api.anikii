import json
import httpx
import asyncio
import random
from typing import Optional
from app.core.config import get_settings

settings = get_settings()

# Async HTTP client (module-level) for connection reuse
_async_client: Optional[httpx.AsyncClient] = None

def _get_async_client() -> httpx.AsyncClient:
    global _async_client
    if _async_client is None:
        timeout = httpx.Timeout(connect=5.0, read=10.0, write=10.0, pool=5.0)
        limits = httpx.Limits(max_keepalive_connections=10, max_connections=50)
        _async_client = httpx.AsyncClient(
            timeout=timeout, 
            limits=limits, 
            follow_redirects=True, 
            headers={
                "User-Agent": "anikii-api/1.0 (+https://github.com/asterixh/anikii)",
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )
    return _async_client

def get_async_client() -> httpx.AsyncClient:
    """Public helper to get the shared client."""
    return _get_async_client()

async def make_api_request_async(body_obj: dict, max_retries: int = 3, backoff_factor: float = 0.3) -> dict:
    """
    Async POST to Anilist GraphQL using httpx.AsyncClient with connection pooling.
    Implements retry with exponential backoff and jitter for transient errors (429/5xx).
    Uses asyncio.timeout for robust timeout management.
    Returns parsed JSON; raises httpx.HTTPError on network/HTTP errors.
    """
    client = get_async_client()
    attempt = 0
    statuses = {429, 500, 502, 503, 504}
    last_exc = None
    
    while attempt <= max_retries:
        try:
            async with asyncio.timeout(10.0):
                resp = await client.post(settings.BASE_URL_ANILIST, json=body_obj)
            
            if resp.status_code in statuses and attempt < max_retries:
                delay = backoff_factor * (2 ** attempt) + random.uniform(0, 0.1)
                await asyncio.sleep(delay)
                attempt += 1
                continue
            resp.raise_for_status()
            try:
                return resp.json()
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Handle cases where response might have a BOM or other issues
                content = resp.content
                # Try to decode with utf-8-sig to handle BOM, and ignore errors as fallback
                text = content.decode('utf-8-sig', errors='ignore')
                return json.loads(text)
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

async def close_async_client():
    """Gracefully close the shared AsyncClient at shutdown."""
    global _async_client
    if _async_client is not None:
        await _async_client.aclose()
        _async_client = None
