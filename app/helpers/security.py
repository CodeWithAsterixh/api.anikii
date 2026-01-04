import os
import socket
from urllib.parse import urlparse
from fastapi import Header, HTTPException, Request
from app.core.config import get_settings
import tempfile

settings = get_settings()
BASE_TMP_DIR = os.path.join(tempfile.gettempdir(), "anikii")

async def verify_api_key(x_api_key: str = Header(None)):
    """Verify the API key for administrative routes."""
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API Key missing")
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

def validate_safe_path(filename: str, base_dir: str = BASE_TMP_DIR) -> str:
    """Validate and return a safe path, preventing path traversal."""
    # Normalize path
    safe_path = os.path.normpath(os.path.join(base_dir, filename))
    # Check if the normalized path starts with the base directory
    if not safe_path.startswith(os.path.abspath(base_dir)):
        raise HTTPException(status_code=400, detail="Invalid path or filename")
    return safe_path

def is_safe_url(url: str) -> bool:
    """
    Check if a URL is safe to fetch (prevents SSRF).
    Blocks local and private IP ranges.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        host = parsed.hostname
        if not host:
            return False
        
        # Resolve hostname to IP
        # Note: In a high-traffic async app, you'd use an async resolver.
        # For this API's current scale, gethostbyname is acceptable during validation.
        ip = socket.gethostbyname(host)
        
        # Private/Reserved IP ranges
        # 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16, 127.0.0.0/8, 169.254.0.0/16, 0.0.0.0
        private_prefixes = (
            "127.", "10.", "192.168.", "169.254.", "0.0.0.0", "localhost"
        )
        if any(ip.startswith(prefix) for prefix in private_prefixes):
            return False
            
        # 172.16.0.0/12 (172.16.x.x to 172.31.x.x)
        if ip.startswith("172."):
            parts = ip.split(".")
            if len(parts) >= 2:
                second_octet = int(parts[1])
                if 16 <= second_octet <= 31:
                    return False
        
        return True
    except Exception:
        return False
