import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, parse_qs
from typing import Dict, List
from .extractors import generate_encrypt_ajax_parameters, decrypt_encrypt_ajax_response  # Replace with actual module

# Constants
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

def get_m3u8(iframe_url: str) -> Dict:
    """
    Retrieves video sources and backup sources from the embedded iframe URL.

    Args:
        iframe_url (str): URL of the iframe containing the video.

    Returns:
        dict: A dictionary containing Referer URL, sources, and backup sources.
    """
    sources = []
    sources_bk = []

    # Parse the iframe URL
    parsed_url = urlparse(iframe_url)
    referer_url = parsed_url.geturl()
    print(f"Fetching URL: {referer_url}")

    # Fetch the iframe page
    response = requests.get(referer_url, headers={"User-Agent": USER_AGENT})
    response.raise_for_status()  # Raise an error for unsuccessful responses
    soup = BeautifulSoup(response.text, "html.parser")

    # Extract the video ID from the iframe URL
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get("id", [None])[0]
    if not video_id:
        raise ValueError("Video ID not found in iframe URL.")

    # Generate encryption parameters
    params = generate_encrypt_ajax_parameters(soup, video_id)

    # Build the encrypt-ajax.php URL
    encrypt_ajax_url = urljoin(
        f"{parsed_url.scheme}://{parsed_url.netloc}", f"encrypt-ajax.php?{params}"
    )

    # Fetch the encrypted response
    ajax_response = requests.get(
        encrypt_ajax_url,
        headers={
            "User-Agent": USER_AGENT,
            "X-Requested-With": "XMLHttpRequest",
        },
    )
    ajax_response.raise_for_status()
    encrypted_data = ajax_response.json()

    # Decrypt the response
    decrypted_response = decrypt_encrypt_ajax_response(encrypted_data)

    # Extract sources and backup sources
    for source in decrypted_response.get("source", []):
        sources.append(source)
    for source_bk in decrypted_response.get("source_bk", []):
        sources_bk.append(source_bk)

    # Log the decrypted response (for debugging purposes)
    print("Decrypted Response:", decrypted_response)

    # Return the result
    return {
        "Referer": referer_url,
        "sources": sources,
        "sources_bk": sources_bk,
    }


