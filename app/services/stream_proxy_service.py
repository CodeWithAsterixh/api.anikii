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

async def stream_video_content(video_url: str, referer: str, filename: str, content_type: str = "video/mp4", disable_ssl: bool = False):
    """Helper for StreamingResponse to proxy video content."""
    if not is_safe_url(video_url):
        logger.warning(f"Blocked unsafe stream URL: {video_url}")
        raise HTTPException(status_code=400, detail="Unsafe stream URL")
        
    headers = {"User-Agent": USER_AGENT, "Referer": referer}
    async with httpx.AsyncClient(timeout=30.0, verify=not disable_ssl, follow_redirects=True) as client:
        try:
            async with client.stream("GET", video_url, headers=headers) as r:
                r.raise_for_status()
                content_length = r.headers.get("Content-Length")
                extra_headers = {"Content-Disposition": f"attachment; filename={filename}.mp4"}
                if content_length:
                    extra_headers["Content-Length"] = content_length
                
                return StreamingResponse(
                    r.aiter_bytes(chunk_size=8192),
                    media_type=r.headers.get("Content-Type", content_type),
                    headers=extra_headers
                )
        except Exception as e:
            logger.error(f"Error streaming video: {e}")
            raise HTTPException(status_code=500, detail="Error fetching video stream")
