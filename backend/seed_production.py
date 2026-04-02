"""
Production seed script for Rebel Trade Network
Creates only the admin account - run once after deployment
"""

import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
import bcrypt
import hashlib
import base64
from cryptography.fernet import Fernet

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Encryption setup (same as server.py)
def get_encryption_key():
    key = os.environ.get("ENCRYPTION_KEY", "default-encryption-key-32b!")
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

fernet = Fernet(get_encryption_key())

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


async def seed_production():
    """Create admin account for production"""
    print("=" * 50)
    print("REBEL TRADE NETWORK - PRODUCTION SEED")
    print("=" * 50)
    
    # Use environment variables for admin credentials
    admin_email = os.environ.get('PROD_ADMIN_EMAIL', 'admin@rebeltrade.network')
    admin_password = os.environ.get('PROD_ADMIN_PASSWORD')
    
    if not admin_password:
        print("ERROR: PROD_ADMIN_PASSWORD environment variable is required")
        print("Set it before running: export PROD_ADMIN_PASSWORD='your-secure-password'")
        return
    
    # Check if admin already exists
    existing = await db.users.find_one({"email": admin_email})
    if existing:
        print(f"\nAdmin account already exists: {admin_email}")
        print("No changes made.")
        return
    
    # Create admin account
    admin_doc = {
        "email": admin_email,
        "password_hash": hash_password(admin_password),
        "name": "Admin",
        "location": encrypt_data(""),
        "bio": encrypt_data("Platform Administrator"),
        "skills": [],
        "goods_offering": [],
        "goods_wanted": [],
        "services_offering": [],
        "services_wanted": [],
        "avatar": "",
        "role": "admin",
        "is_verified": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.users.insert_one(admin_doc)
    
    print(f"\nAdmin account created successfully!")
    print(f"  Email: {admin_email}")
    print(f"  Role: admin")
    print(f"  ID: {result.inserted_id}")
    print("\nYou can now:")
    print("  1. Log in with your admin credentials")
    print("  2. Use 'Invite Members' to invite your first users")
    print("  3. Update your profile with location and skills")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    asyncio.run(seed_production())
