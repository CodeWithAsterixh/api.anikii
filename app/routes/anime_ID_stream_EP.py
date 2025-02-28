import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import asyncio
import subprocess
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
import urllib3
from typing import Optional
import ffmpeg  # ffmpeg-python library

# Disable SSL warnings (for testing; in production configure certificates properly)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"

from app.helpers.streamInfoSc import parse_streaming_info
from app.helpers.modules import fetch_malsyn_data_and_get_provider
from app.helpers.base import BASEURL
from app.helpers.scrapers.mp4Up import getVid

router = APIRouter(prefix="/anime", tags=["id", "ep"])

@router.get("/{id}/stream/ep/{ep}")
async def fetch_streaming_info(id: int, ep: int):
    try:
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoSub = idSub["id_provider"]["idGogo"]
        urlSub = f"{BASEURL}/{gogoSub}-episode-{ep}"
        try:
            episode_dataSub = parse_streaming_info(urlSub)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {"error": "Sub episode not found", "episode": ep}, 404
            else:
                raise
        return episode_dataSub, 200
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

# Download endpoint with optional resolution parameter (360-1080).
@router.get("/{id}/stream/ep/{ep}/download")
async def download_streaming_video(
    id: int, 
    ep: int, 
    resolution: Optional[int] = Query(
        None, ge=360, le=1080, 
        description="Desired video height in pixels (e.g., 360, 480, 720, or 1080). If not provided, original quality is streamed."
    )
):
    try:
        # Fetch provider data and build URL for the episode.
        idSub = await fetch_malsyn_data_and_get_provider(id)
        gogoSub = idSub["id_provider"]["idGogo"]
        urlSub = f"{BASEURL}/{gogoSub}-episode-{ep}"
        
        # Fetch and parse streaming info.
        try:
            episode_dataSub = parse_streaming_info(urlSub)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail=f"Sub episode not found: {ep}")
            else:
                raise

        # Extract the mp4upload link from the stream_links list.
        mp4upload_link = next((link.url for link in episode_dataSub.stream_links if link.name == "mp4upload"), None)
        if not mp4upload_link:
            raise HTTPException(status_code=404, detail="mp4upload link not found")
        
        # Extract direct video URL using getVid.
        video_url = await getVid(mp4upload_link)
        if not video_url:
            raise HTTPException(status_code=500, detail="Failed to extract video URL")
        
        # Set headers for fetching the video.
        headers = {
            "User-Agent": USER_AGENT,
            "Referer": mp4upload_link
        }
        
        if resolution is not None:
            # Use ffmpeg-python to transcode on the fly to the desired resolution.
            # We pass HTTP headers to ffmpeg via the "headers" parameter.
            try:
                # Construct a headers string (each header separated by CRLF).
                ffmpeg_headers = f"User-Agent: {USER_AGENT}\r\nReferer: {mp4upload_link}\r\n"
                process = (
                    ffmpeg
                    .input(video_url, headers=ffmpeg_headers)
                    .filter('scale', -2, resolution)
                    .output('pipe:1', format='mp4', vcodec='libx264', preset='fast', video_bitrate='800k', acodec='aac', audio_bitrate='128k')
                    .run_async(pipe_stdout=True, pipe_stderr=True)
                )
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error starting ffmpeg-python: {e}")
            
            def iter_transcoded():
                try:
                    while True:
                        chunk = process.stdout.read(8192)
                        if not chunk:
                            break
                        yield chunk
                finally:
                    process.stdout.close()
                    process.wait()
            
            return StreamingResponse(
                iter_transcoded(),
                media_type="video/mp4",
                headers={"Content-Disposition": f"attachment; filename=video_{resolution}.mp4"}
            )
        else:
            # Stream the original video without transcoding.
            try:
                r = requests.get(video_url, headers=headers, stream=True, timeout=30, verify=False)
                r.raise_for_status()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error fetching video: {e}")

            # Include Content-Length header if available.
            content_length = r.headers.get("Content-Length")
            extra_headers = {"Content-Disposition": "attachment; filename=video.mp4"}
            if content_length:
                extra_headers["Content-Length"] = content_length

            def iter_content():
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        yield chunk

            return StreamingResponse(
                iter_content(),
                media_type=r.headers.get("Content-Type", "application/octet-stream"),
                headers=extra_headers
            )
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
