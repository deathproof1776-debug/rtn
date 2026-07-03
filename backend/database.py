"""
Database connection and encryption utilities for Rebel Trade Network.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from cryptography.fernet import Fernet
import os
import base64
import hashlib

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


# Encryption setup
def get_encryption_key():
    key = os.environ["ENCRYPTION_KEY"]
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


fernet = Fernet(get_encryption_key())


def encrypt_data(data: str) -> str:
    """Encrypt a string using Fernet symmetric encryption."""
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt a Fernet-encrypted string."""
    return fernet.decrypt(encrypted_data.encode()).decode()


def safe_decrypt(value, fallback: str = "") -> str:
    """Decrypt a Fernet value silently. Returns the original value if decryption fails,
    or `fallback` if the value is empty/None."""
    if not value:
        return fallback
    try:
        return fernet.decrypt(value.encode()).decode()
    except Exception:
        return value if isinstance(value, str) else fallback
