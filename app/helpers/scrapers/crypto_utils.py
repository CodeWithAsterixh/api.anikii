from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64
import json
from app.core.logger import logger

def decrypt_sources(encrypted_data, decryption_key):
    try:
        raw = base64.b64decode(encrypted_data)

        nonce = raw[:12]
        tag = raw[12:28]
        ciphertext = raw[28:]

        key_bytes = decryption_key.encode("utf-8")
        cipher = AES.new(key_bytes, AES.MODE_GCM, nonce=nonce)

        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return json.loads(plaintext.decode("utf-8"))
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        return []
