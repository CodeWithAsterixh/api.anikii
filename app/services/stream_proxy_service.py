import logging
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from app.helpers.security import is_safe_url

logger = logging.getLogger(__name__)

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/112.0.0.0 Safari/537.36"
)

def stream_video_content(video_url: str, referer: str, file_name: str, content_type: str = "video/mp4", disable_ssl: bool = False):
    """Helper for StreamingResponse to proxy video content with proper connection management."""
    if not is_safe_url(video_url):
        logger.warning(f"Blocked unsafe stream URL: {video_url}")
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
        headers={"Content-Disposition": f"attachment; file_name={file_name}.mp4"}
    )
