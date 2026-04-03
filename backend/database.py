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
    key = os.environ.get("ENCRYPTION_KEY", "default-encryption-key-32b!")
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)


fernet = Fernet(get_encryption_key())


def encrypt_data(data: str) -> str:
    """Encrypt a string using Fernet symmetric encryption."""
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt a Fernet-encrypted string."""
    return fernet.decrypt(encrypted_data.encode()).decode()
