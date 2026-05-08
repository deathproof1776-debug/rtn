"""
WebSocket handler for real-time messaging.
"""
import json
from datetime import datetime, timezone

import jwt as pyjwt
from bson import ObjectId
from fastapi import WebSocket, WebSocketDisconnect

from database import db, encrypt_data
from auth import get_jwt_secret, JWT_ALGORITHM
from websocket_manager import manager


async def _authenticate_ws(websocket: WebSocket, user_id: str) -> bool:
    """Validate the JWT token (with legacy user_id fallback). Returns True if authorized."""
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return False
    try:
        payload = pyjwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access" or payload.get("sub") != user_id:
            await websocket.close(code=4001)
            return False
        return True
    except pyjwt.InvalidTokenError:
        # Fallback: legacy user_id token for backwards compatibility
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user or token != user_id:
            await websocket.close(code=4001)
            return False
        return True


async def _persist_and_relay_message(user_id: str, websocket: WebSocket, payload: dict) -> None:
    receiver_id = payload.get("receiver_id")
    content = payload.get("content")
    if not receiver_id or not content:
        return

    msg_doc = {
        "sender_id": user_id,
        "receiver_id": receiver_id,
        "content": encrypt_data(content),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False,
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
        "created_at": msg_doc["created_at"],
    }, receiver_id)

    await websocket.send_json({
        "type": "message_sent",
        "id": str(result.inserted_id),
        "receiver_id": receiver_id,
        "content": content,
        "created_at": msg_doc["created_at"],
    })


async def handle_websocket(websocket: WebSocket, user_id: str) -> None:
    """Handle WebSocket connections for real-time messaging."""
    if not await _authenticate_ws(websocket, user_id):
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            msg_type = message_data.get("type")
            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
            elif msg_type == "message":
                await _persist_and_relay_message(user_id, websocket, message_data)
    except WebSocketDisconnect:
        manager.disconnect(user_id)
