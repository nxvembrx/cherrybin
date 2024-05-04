import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV

NONCE_SIZE_BYTES = 12

key = base64.b64decode(bytes(os.environ.get("ENCRYPTION_KEY"), "utf-8"))
aesgcmsiv = AESGCMSIV(key)


def encrypt_paste(paste_name, paste_contents):
    return encrypt(paste_name), encrypt(paste_contents)


def decrypt_paste(paste_name_enc, paste_contents_enc):
    return decrypt(paste_name_enc), decrypt(paste_contents_enc)


def encrypt(plaintext):
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = aesgcmsiv.encrypt(nonce, plaintext.encode(), None)

    return base64.b64encode(bytearray(nonce + ciphertext)).decode()


def decrypt(ciphertext):
    ciphertext_dec = base64.b64decode(ciphertext.encode())
    nonce = ciphertext_dec[:12]
    text = ciphertext_dec[12:]

    return aesgcmsiv.decrypt(nonce, text, None).decode()
