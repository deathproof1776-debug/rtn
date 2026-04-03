"""
Messaging routes: conversations and direct messages.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from models import MessageCreate
from notifications import send_push_notification
from websocket_manager import manager

router = APIRouter()


@router.get("/conversations")
async def get_conversations(request: Request):
    user = await get_current_user(request)
    user_id = user["_id"]

    pipeline = [
        {"$match": {"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"$cond": [{"$eq": ["$sender_id", user_id]}, "$receiver_id", "$sender_id"]},
            "last_message": {"$first": "$content"},
            "last_message_at": {"$first": "$created_at"},
            "unread_count": {"$sum": {"$cond": [{"$and": [{"$eq": ["$receiver_id", user_id]}, {"$eq": ["$read", False]}]}, 1, 0]}}
        }}
    ]

    conversations = await db.messages.aggregate(pipeline).to_list(50)

    result = []
    for conv in conversations:
        other_user = await db.users.find_one({"_id": ObjectId(conv["_id"])}, {"password_hash": 0})
        if other_user:
            last_msg = conv.get("last_message", "")
            try:
                last_msg = decrypt_data(last_msg)
            except Exception:
                pass

            result.append({
                "user_id": str(other_user["_id"]),
                "user_name": other_user.get("name", "Unknown"),
                "user_avatar": other_user.get("avatar", ""),
                "last_message": last_msg[:50] + "..." if len(last_msg) > 50 else last_msg,
                "last_message_at": conv.get("last_message_at"),
                "unread_count": conv.get("unread_count", 0)
            })

    return result


@router.get("/messages/{other_user_id}")
async def get_messages(other_user_id: str, request: Request, skip: int = 0, limit: int = 50):
    user = await get_current_user(request)
    user_id = user["_id"]

    messages = await db.messages.find({
        "$or": [
            {"sender_id": user_id, "receiver_id": other_user_id},
            {"sender_id": other_user_id, "receiver_id": user_id}
        ]
    }).sort("created_at", 1).skip(skip).limit(limit).to_list(limit)

    # Mark messages as read
    await db.messages.update_many(
        {"sender_id": other_user_id, "receiver_id": user_id, "read": False},
        {"$set": {"read": True}}
    )

    result = []
    for msg in messages:
        content = msg.get("content", "")
        try:
            content = decrypt_data(content)
        except Exception:
            pass
        result.append({
            "id": str(msg["_id"]),
            "sender_id": msg["sender_id"],
            "receiver_id": msg["receiver_id"],
            "content": content,
            "created_at": msg["created_at"],
            "read": msg.get("read", False)
        })

    return result


@router.post("/messages")
async def send_message(message: MessageCreate, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)

    msg_doc = {
        "sender_id": user["_id"],
        "receiver_id": message.receiver_id,
        "content": encrypt_data(message.content),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    result = await db.messages.insert_one(msg_doc)

    # Send via WebSocket if receiver is connected
    await manager.send_personal_message({
        "type": "new_message",
        "id": str(result.inserted_id),
        "sender_id": user["_id"],
        "sender_name": user.get("name", "Unknown"),
        "content": message.content,
        "created_at": msg_doc["created_at"]
    }, message.receiver_id)

    # Send push notification
    background_tasks.add_task(
        send_push_notification,
        user_id=message.receiver_id,
        title=f"New message from {user.get('name', 'Someone')}",
        body=message.content[:100] + ("..." if len(message.content) > 100 else ""),
        data={"type": "message", "sender_id": user["_id"], "url": "/messages"}
    )

    return {"id": str(result.inserted_id), "message": "Message sent"}
