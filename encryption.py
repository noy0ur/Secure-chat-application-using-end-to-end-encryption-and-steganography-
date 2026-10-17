from Crypto.Cipher import AES
import base64
import hashlib

def get_key(key):
    return hashlib.sha256(key.encode()).digest()

def encrypt_message(message, key):
    key = get_key(key)

    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce

    ciphertext, tag = cipher.encrypt_and_digest(message.encode())

    return base64.b64encode(nonce + tag + ciphertext).decode()

def decrypt_message(encrypted_data, key):
    key = get_key(key)

    try:
        data = base64.b64decode(encrypted_data)

        nonce = data[:16]
        tag = data[16:32]
        ciphertext = data[32:]

        cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)

        decrypted = cipher.decrypt_and_verify(ciphertext, tag)
        return decrypted.decode()

    except:
        return "Decryption Failed!"
