"""
Admin routes: user management, platform stats, moderation, system messages.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from database import db, safe_decrypt
from auth import require_admin
from models import VerifyTraderRequest, UpdateUserRole
from achievements import grant_achievement

router = APIRouter(prefix="/admin")


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def log_admin_action(admin: dict, action: str, target_type: str,
                           target_id: str, target_name: str, details: str = ""):
    await db.audit_log.insert_one({
        "admin_id": admin["_id"],
        "admin_name": admin.get("name", "Admin"),
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "target_name": target_name,
        "details": details,
        "created_at": _now_iso(),
    })


@router.post("/verify-trader")
async def verify_trader(data: VerifyTraderRequest, admin: dict = Depends(require_admin)):
    target = await db.users.find_one({"_id": ObjectId(data.user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one(
        {"_id": ObjectId(data.user_id)},
        {"$set": {"is_verified": data.is_verified}}
    )
    # Celebrate a newly-granted verification (only on transition to verified)
    if data.is_verified and not target.get("is_verified"):
        await grant_achievement(data.user_id, "verified")
    await log_admin_action(
        admin, "verified" if data.is_verified else "unverified", "user",
        data.user_id, target.get("name", "Unknown"),
        f"Verification status changed to {data.is_verified}"
    )
    return {
        "message": f"User {'verified' if data.is_verified else 'unverified'} successfully",
        "user_id": data.user_id,
        "is_verified": data.is_verified,
    }


@router.get("/audit-log")
async def get_audit_log(skip: int = 0, limit: int = 50, _: dict = Depends(require_admin)):
    logs = await db.audit_log.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for log in logs:
        log["_id"] = str(log["_id"])
    total = await db.audit_log.count_documents({})
    return {"logs": logs, "total": total}


@router.get("/users")
async def get_admin_users(skip: int = 0, limit: int = 50, _: dict = Depends(require_admin)):
    users = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for user in users:
        user["_id"] = str(user["_id"])
        user["location"] = safe_decrypt(user.get("location"))
        user["bio"] = safe_decrypt(user.get("bio"))
    total = await db.users.count_documents({})
    return {"users": users, "total": total}


@router.get("/stats")
async def get_admin_stats(_: dict = Depends(require_admin)):
    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    return {
        "total_users": await db.users.count_documents({}),
        "verified_users": await db.users.count_documents({"is_verified": True}),
        "trusted_users": await db.users.count_documents({"is_trusted_trader": True}),
        "moderator_users": await db.users.count_documents({"role": "moderator"}),
        "total_posts": await db.posts.count_documents({}),
        "total_messages": await db.messages.count_documents({}),
        "total_connections": await db.network_connections.count_documents({}),
        "pending_requests": await db.network_requests.count_documents({"status": "pending"}),
        "total_invites": await db.invites.count_documents({}),
        "used_invites": await db.invites.count_documents({"used": True}),
        "new_users_week": await db.users.count_documents({"created_at": {"$gte": week_ago}}),
        "new_posts_week": await db.posts.count_documents({"created_at": {"$gte": week_ago}}),
    }


@router.get("/posts")
async def get_admin_posts(skip: int = 0, limit: int = 50, _: dict = Depends(require_admin)):
    posts = await db.posts.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for post in posts:
        post["_id"] = str(post["_id"])
        post["description"] = safe_decrypt(post.get("description"))
        for comment in post.get("comments") or []:
            comment["content"] = safe_decrypt(comment.get("content"))
    total = await db.posts.count_documents({})
    return {"posts": posts, "total": total}


@router.delete("/posts/{post_id}")
async def admin_delete_post(post_id: str, admin: dict = Depends(require_admin)):
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    await db.posts.delete_one({"_id": ObjectId(post_id)})
    await log_admin_action(
        admin, "deleted_post", "post", post_id,
        post.get("title", "Unknown Post"),
        f"Post by {post.get('user_name', 'Unknown')} deleted"
    )
    return {"message": "Post deleted successfully"}


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, data: UpdateUserRole,
                           admin: dict = Depends(require_admin)):
    if data.role not in ["admin", "moderator", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")
    # Hybrid rule: only verified traders are eligible to be moderators
    if data.role == "moderator" and not target.get("is_verified"):
        raise HTTPException(
            status_code=400,
            detail="Only verified traders can be promoted to moderator. Verify this user first."
        )
    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": data.role}})
    # Celebrate a newly-granted moderator role (only on transition)
    if data.role == "moderator" and target.get("role") != "moderator":
        await grant_achievement(user_id, "moderator")
    await log_admin_action(
        admin, "role_changed", "user", user_id, target.get("name", "Unknown"),
        f"Role changed from {target.get('role', 'user')} to {data.role}"
    )
    return {"message": f"User role updated to {data.role}", "user_id": user_id, "role": data.role}


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: str, admin: dict = Depends(require_admin)):
    if user_id == admin["_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")
    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.posts.delete_many({"user_id": user_id})
    await db.messages.delete_many({"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]})
    await db.network_connections.delete_many(
        {"$or": [{"user_id": user_id}, {"connected_user_id": user_id}]}
    )
    await db.network_requests.delete_many(
        {"$or": [{"from_user_id": user_id}, {"to_user_id": user_id}]}
    )
    await db.push_subscriptions.delete_many({"user_id": user_id})

    await log_admin_action(
        admin, "deleted_user", "user", user_id, target.get("name", "Unknown"),
        f"User {target.get('email', '')} and all associated data deleted"
    )
    return {"message": "User and all associated data deleted"}


# ========================
# System Messages (Banner Announcements)
# ========================
VALID_TYPES = ["info", "warning", "success", "urgent"]


@router.post("/system-messages")
async def create_system_message(request: Request, admin: dict = Depends(require_admin)):
    data = await request.json()
    message = (data.get("message") or "").strip()
    if not message:
        raise HTTPException(status_code=400, detail="Message content is required")

    msg_type = data.get("type", "info")
    if msg_type not in VALID_TYPES:
        msg_type = "info"

    msg_doc = {
        "message": message,
        "type": msg_type,
        "is_active": data.get("is_active", True),
        "priority": data.get("priority", 0),
        "created_by": admin["_id"],
        "created_by_name": admin.get("name", "Admin"),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    result = await db.system_messages.insert_one(msg_doc)
    await log_admin_action(
        admin, "created_system_message", "system_message",
        str(result.inserted_id), message[:50],
        f"Type: {msg_type}, Active: {msg_doc['is_active']}"
    )
    return {"id": str(result.inserted_id), "message": "System message created"}


@router.get("/system-messages")
async def get_all_system_messages(skip: int = 0, limit: int = 50,
                                  _: dict = Depends(require_admin)):
    messages = await db.system_messages.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    total = await db.system_messages.count_documents({})
    return {"messages": messages, "total": total}


@router.put("/system-messages/{message_id}")
async def update_system_message(message_id: str, request: Request,
                                admin: dict = Depends(require_admin)):
    data = await request.json()
    msg = await db.system_messages.find_one({"_id": ObjectId(message_id)})
    if not msg:
        raise HTTPException(status_code=404, detail="System message not found")

    update_data: dict = {"updated_at": _now_iso()}
    if "message" in data:
        update_data["message"] = data["message"].strip()
    if "type" in data and data["type"] in VALID_TYPES:
        update_data["type"] = data["type"]
    if "is_active" in data:
        update_data["is_active"] = bool(data["is_active"])
    if "priority" in data:
        update_data["priority"] = int(data["priority"])

    await db.system_messages.update_one({"_id": ObjectId(message_id)}, {"$set": update_data})
    await log_admin_action(
        admin, "updated_system_message", "system_message", message_id,
        msg.get("message", "")[:50],
        f"Updated fields: {list(update_data.keys())}"
    )
    return {"message": "System message updated"}


@router.delete("/system-messages/{message_id}")
async def delete_system_message(message_id: str, admin: dict = Depends(require_admin)):
    msg = await db.system_messages.find_one({"_id": ObjectId(message_id)})
    if not msg:
        raise HTTPException(status_code=404, detail="System message not found")
    await db.system_messages.delete_one({"_id": ObjectId(message_id)})
    await log_admin_action(
        admin, "deleted_system_message", "system_message", message_id,
        msg.get("message", "")[:50], ""
    )
    return {"message": "System message deleted"}


# Public: list active system messages (no auth required)
@router.get("/system-messages/active", tags=["Public"])
async def get_active_system_messages():
    messages = await db.system_messages.find(
        {"is_active": True},
        {"_id": 1, "message": 1, "type": 1, "priority": 1}
    ).sort("priority", -1).limit(10).to_list(10)
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    return {"messages": messages}
