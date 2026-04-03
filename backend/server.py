"""
Rebel Trade Network - Main FastAPI Application

This is the refactored entry point that imports modular routes from /routes/.
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import json
import logging
from datetime import datetime, timezone

from database import db, client, encrypt_data
from auth import hash_password, verify_password
from routes import api_router
from websocket_manager import manager
from storage import init_storage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create app
app = FastAPI(title="Rebel Trade Network API")

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


async def handle_websocket(websocket: WebSocket, user_id: str):
    """Handle WebSocket connections for real-time messaging"""
    from bson import ObjectId
    import jwt as pyjwt
    from auth import get_jwt_secret, JWT_ALGORITHM
    
    # Verify JWT token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    # Validate JWT token
    try:
        payload = pyjwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            await websocket.close(code=4001)
            return
        token_user_id = payload.get("sub")
        if token_user_id != user_id:
            await websocket.close(code=4001)
            return
    except pyjwt.InvalidTokenError:
        # Fallback to legacy user_id token for backwards compatibility
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user or token != user_id:
            await websocket.close(code=4001)
            return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            if message_data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message_data.get("type") == "message":
                receiver_id = message_data.get("receiver_id")
                content = message_data.get("content")

                if receiver_id and content:
                    msg_doc = {
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "content": encrypt_data(content),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "read": False
                    }
                    result = await db.messages.insert_one(msg_doc)

                    sender = await db.users.find_one({"_id": ObjectId(user_id)})
                    sender_name = sender.get("name", "Unknown") if sender else "Unknown"

                    await manager.send_personal_message({
                        "type": "new_message",
                        "id": str(result.inserted_id),
                        "sender_id": user_id,
                        "sender_name": sender_name,
                        "content": content,
                        "created_at": msg_doc["created_at"]
                    }, receiver_id)

                    await websocket.send_json({
                        "type": "message_sent",
                        "id": str(result.inserted_id),
                        "receiver_id": receiver_id,
                        "content": content,
                        "created_at": msg_doc["created_at"]
                    })
    except WebSocketDisconnect:
        manager.disconnect(user_id)


# ========================
# CORS Configuration
# ========================

cors_origins = os.environ.get("CORS_ORIGINS", "*")
if cors_origins == "*":
    allow_origins_list = ["*"]
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
