import logging
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.helpers.security import is_safe_url
from urllib.parse import urlparse
import ipaddress
import socket

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

def _is_public_http_url(url: str) -> bool:
    """
    Ensure the URL uses HTTP(S) and resolves only to public IP addresses.
    This is a defense-in-depth check against SSRF.
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False

    hostname = parsed.hostname
    if not hostname:
        return False

    try:
        addrinfo_list = socket.getaddrinfo(hostname, None)
    except OSError:
        # Host could not be resolved; treat as unsafe.
        return False

    for family, _, _, _, sockaddr in addrinfo_list:
        ip_str = None
        if family == socket.AF_INET:
            ip_str = sockaddr[0]
        elif family == socket.AF_INET6:
            ip_str = sockaddr[0]

        if not ip_str:
            continue

        try:
            ip_obj = ipaddress.ip_address(ip_str)
        except ValueError:
            return False

        if (
            ip_obj.is_private
            or ip_obj.is_loopback
            or ip_obj.is_link_local
            or ip_obj.is_multicast
            or ip_obj.is_reserved
        ):
            # Reject any URL that resolves to a non-public address.
            return False

    return True

async def stream_video_content(video_url: str, referer: str, filename: str, content_type: str = "video/mp4", disable_ssl: bool = False):
    """Helper for StreamingResponse to proxy video content with proper connection management."""
    if not is_safe_url(video_url):
        logger.warning(f"Blocked unsafe stream URL (failed is_safe_url): {video_url}")
        raise HTTPException(status_code=400, detail="Unsafe stream URL")

    if not _is_public_http_url(video_url):
        logger.warning(f"Blocked unsafe stream URL (non-public or non-HTTP): {video_url}")
        raise HTTPException(status_code=400, detail="Unsafe stream URL")

    headers = {"User-Agent": USER_AGENT, "Referer": referer}

    async def generate_chunks():
        async with httpx.AsyncClient(timeout=60.0, verify=not disable_ssl, follow_redirects=True) as client:
            try:
                async with client.stream("GET", video_url, headers=headers) as r:
                    r.raise_for_status()
                    async for chunk in r.aiter_bytes(chunk_size=65536):
                        yield chunk
            except Exception as e:
                logger.error(f"Error during video streaming: {e}")
                # We can't raise HTTPException here as the response has already started
                return

    # We need to get headers (like Content-Length) before returning the response
    # but that would require a separate HEAD request or opening the stream twice.
    # For now, we'll return the StreamingResponse directly.
    return StreamingResponse(
        generate_chunks(),
        media_type=content_type,
        headers={"Content-Disposition": f"attachment; filename={filename}.mp4"}
    )
