from Crypto.Cipher import AES
import base64
import json
import os
from app.core.config import get_settings

settings = get_settings()

def encrypt_aes(data: str, key: bytes, iv: bytes) -> str:
    """
    Encrypts the input data using AES-GCM encryption with the specified key.
    Note: The 'iv' parameter is kept for signature compatibility but GCM 
    uses a random nonce for better security.

    Args:
        data (str): The plaintext data to encrypt.
        key (bytes): The AES key for encryption.
        iv (bytes): The Initialization Vector (used as fallback nonce if needed).

    Returns:
        str: Base64 encoded encrypted data (nonce + tag + ciphertext).
    """
    # Use GCM mode for better security (addresses SonarQube python:S5542)
    # Explicitly use a 12-byte nonce as recommended for GCM
    cipher = AES.new(key, AES.MODE_GCM, nonce=os.urandom(12))
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    
    # Combine nonce, tag, and ciphertext for the result
    result = cipher.nonce + tag + ciphertext
    return base64.b64encode(result).decode('utf-8')

def decrypt_aes(data: str, key: bytes, iv: bytes) -> str:
    """
    Decrypts AES-GCM encrypted data with the specified key.

    Args:
        data (str): The Base64 encoded encrypted data (nonce + tag + ciphertext).
        key (bytes): The AES key for decryption.
        iv (bytes): The Initialization Vector (unused in GCM if nonce is in data).

    Returns:
        str: The decrypted plaintext data.
    """
    try:
        raw = base64.b64decode(data)
        # Using 12-byte nonce and 16-byte tag (standard for GCM)
        nonce = raw[:12]
        tag = raw[12:28]
        ciphertext = raw[28:]
        
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        decrypted_bytes = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted_bytes.decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"AES Decryption error: {e}")
        return ""

def generate_encrypt_ajax_parameters(script_data: str, video_id: str) -> str:
    """
    Generates the parameters required for `encrypt-ajax.php` by encrypting the video ID
    and decrypting the embedded token from the provided script data.

    Args:
        script_data (str): The data value from the script tag in the embedded video page.
        video_id (str): The ID of the embedded video URL.

    Returns:
        str: Formatted parameters for the `encrypt-ajax.php` request.
    """
    # Encrypt the video ID
    encrypted_key = encrypt_aes(video_id, settings.AES_KEY, settings.AES_IV)

    # Decrypt the embedded token
    token = decrypt_aes(script_data, settings.AES_KEY, settings.AES_IV)

    # Generate and return the parameters string
    return f"id={encrypted_key}&alias={video_id}&{token}"

def decrypt_encrypt_ajax_response(response_data: dict) -> dict:
    """
    Decrypts the response from `encrypt-ajax.php`.

    Args:
        response_data (dict): The server's response containing encrypted data.

    Returns:
        dict: The decrypted JSON object.
    """
    encrypted_data = response_data.get('data')
    if not encrypted_data:
        raise ValueError("Response data does not contain 'data' key.")

    # Decrypt the encrypted data
    decrypted_str = decrypt_aes(encrypted_data, settings.AES_SECOND_KEY, settings.AES_IV)

    # Parse and return as a dictionary
    return json.loads(decrypted_str)


