import os
import socket
import ipaddress
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
    Blocks local and private IP ranges using robust CIDR checks.
    """
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        
        host = parsed.hostname
        if not host:
            return False
        
        # 1. Check if host is an IP address string directly
        try:
            ip = ipaddress.ip_address(host)
            if _is_ip_unsafe(ip):
                return False
            return True
        except ValueError:
            # Not an IP string, proceed to DNS resolution
            pass

        # 2. Resolve hostname to all possible IPs (IPv4 and IPv6)
        try:
            # getaddrinfo returns a list of tuples: (family, type, proto, canonname, sockaddr)
            # sockaddr is (address, port) for IPv4/v6
            addr_info = socket.getaddrinfo(host, None)
            for item in addr_info:
                ip_str = item[4][0]
                ip = ipaddress.ip_address(ip_str)
                if _is_ip_unsafe(ip):
                    return False
        except socket.gaierror:
            return False
            
        return True
    except Exception:
        return False

def _is_ip_unsafe(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> bool:
    """Check if an IP address is private, loopback, link-local, or otherwise unsafe."""
    return (
        ip.is_private or 
        ip.is_loopback or 
        ip.is_link_local or 
        ip.is_multicast or 
        ip.is_reserved or 
        ip.is_unspecified
    )
