from Crypto.Cipher import AES
import base64
import json

def decrypt_sources(encrypted_data, decryption_key):
    try:
        key_bytes = decryption_key.encode('utf-8')
        cipher = AES.new(key_bytes, AES.MODE_ECB)
        decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
        # Remove potential padding and handle possible decoding issues
        decrypted_text = decrypted.decode('utf-8', errors='ignore').strip()
        # Find the first '{' and last '}' to isolate JSON if there's garbage
        start_index = decrypted_text.find('{')
        end_index = decrypted_text.rfind('}')
        if start_index != -1 and end_index != -1:
            decrypted_text = decrypted_text[start_index:end_index+1]
        return json.loads(decrypted_text)
    except Exception as e:
        print(f"Decryption error: {e}")
        return []
