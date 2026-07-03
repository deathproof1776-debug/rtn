"""
Rebel Trade Network - Main FastAPI Application

This is the refactored entry point that imports modular routes from /routes/.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import logging
from datetime import datetime, timezone

from database import db, client
from auth import hash_password, verify_password
from routes import api_router
from storage import init_storage
from security import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from websocket_handlers import handle_websocket

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Rebel Trade Network API")

# Rate limiter setup
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Include the modular API router
app.include_router(api_router)


# ========================
# WebSocket Endpoints
# ========================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await handle_websocket(websocket, user_id)


@app.websocket("/api/ws/{user_id}")
async def api_websocket_endpoint(websocket: WebSocket, user_id: str):
    await handle_websocket(websocket, user_id)


# ========================
# CORS Configuration
# ========================

cors_origins = os.environ.get("CORS_ORIGINS", "*")
if cors_origins == "*":
    # Credentialed (cookie) auth is NOT allowed with a literal "*" origin per the
    # CORS spec — browsers block the response. Reflect the request origin instead
    # so cross-origin cookie auth works for any deployment domain.
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origin_regex=".*",
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    allow_origins_list = [origin.strip() for origin in cors_origins.split(",")]
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=allow_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )


# ========================
# Startup & Shutdown Events
# ========================

@app.on_event("startup")
async def startup():
    # Initialize object storage
    try:
        init_storage()
        logger.info("Object storage initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize object storage: {e}")

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.messages.create_index([("sender_id", 1), ("receiver_id", 1)])
    await db.posts.create_index("created_at")
    await db.posts.create_index("category")
    await db.push_subscriptions.create_index([("user_id", 1), ("endpoint", 1)], unique=True)
    await db.network_connections.create_index([("user_id", 1), ("connected_user_id", 1)], unique=True)
    await db.network_requests.create_index([("from_user_id", 1), ("to_user_id", 1)])
    await db.network_requests.create_index("status")
    await db.audit_log.create_index("created_at")
    await db.trade_deals.create_index([("proposer_id", 1), ("status", 1)])
    await db.trade_deals.create_index([("receiver_id", 1), ("status", 1)])
    await db.trade_deals.create_index("updated_at")
    await db.gallery.create_index([("user_id", 1), ("created_at", -1)])
    await db.gallery.create_index("is_deleted")
    # Community Board indexes
    await db.community_posts.create_index([("created_at", -1)])
    await db.community_posts.create_index("topic")
    await db.community_posts.create_index("is_deleted")
    # System Messages indexes
    await db.system_messages.create_index("is_active")
    await db.system_messages.create_index("priority")
    # Security collections
    await db.login_attempts.create_index("email", unique=True)
    await db.refresh_tokens.create_index("token_hash", unique=True)
    await db.refresh_tokens.create_index("user_id")
    await db.refresh_tokens.create_index("session_id")
    await db.recovery_codes.create_index("user_id")
    # Moderation collections
    await db.blocks.create_index([("blocker_id", 1), ("blocked_id", 1)], unique=True)
    await db.blocks.create_index("blocked_id")
    await db.reports.create_index([("status", 1), ("created_at", -1)])
    await db.reports.create_index([("reporter_id", 1), ("target_type", 1), ("target_id", 1), ("status", 1)])

    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@rebeltrade.network")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})

    if existing is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hashed,
            "name": "Admin",
            "location": "",
            "bio": "",
            "skills": ["Community Management", "Trading"],
            "goods_offering": [],
            "goods_wanted": [],
            "services_offering": [],
            "services_wanted": [],
            "avatar": "",
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
        logger.info("Admin password updated")

    # Write test credentials
    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write("## Admin Account\n")
        f.write(f"- Email: {admin_email}\n")
        f.write(f"- Password: {admin_password}\n")
        f.write("- Role: admin\n\n")
        f.write("## Auth Endpoints\n")
        f.write("- POST /api/auth/register\n")
        f.write("- POST /api/auth/login\n")
        f.write("- POST /api/auth/logout\n")
        f.write("- GET /api/auth/me\n")
        f.write("- POST /api/auth/refresh\n")


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
