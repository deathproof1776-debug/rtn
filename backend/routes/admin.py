"""
Admin routes: user management, platform stats, moderation.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from database import db, decrypt_data
from auth import get_current_user, hash_password, verify_password
from models import VerifyTraderRequest, UpdateUserRole

router = APIRouter(prefix="/admin")


async def log_admin_action(
    admin_id: str,
    admin_name: str,
    action: str,
    target_type: str,
    target_id: str,
    target_name: str,
    details: str = ""
):
    """Log admin actions for audit trail"""
    await db.audit_log.insert_one({
        "admin_id": admin_id,
        "admin_name": admin_name,
        "action": action,
        "target_type": target_type,
        "target_id": target_id,
        "target_name": target_name,
        "details": details,
        "created_at": datetime.now(timezone.utc).isoformat()
    })


@router.post("/verify-trader")
async def verify_trader(data: VerifyTraderRequest, request: Request):
    """Admin endpoint to verify/unverify a trader"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    target = await db.users.find_one({"_id": ObjectId(data.user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one(
        {"_id": ObjectId(data.user_id)},
        {"$set": {"is_verified": data.is_verified}}
    )

    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="verified" if data.is_verified else "unverified",
        target_type="user",
        target_id=data.user_id,
        target_name=target.get("name", "Unknown"),
        details=f"Verification status changed to {data.is_verified}"
    )

    return {
        "message": f"User {'verified' if data.is_verified else 'unverified'} successfully",
        "user_id": data.user_id,
        "is_verified": data.is_verified
    }


@router.get("/audit-log")
async def get_audit_log(request: Request, skip: int = 0, limit: int = 50):
    """Get admin audit log"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    logs = await db.audit_log.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for log in logs:
        log["_id"] = str(log["_id"])

    total = await db.audit_log.count_documents({})
    return {"logs": logs, "total": total}


@router.get("/users")
async def get_admin_users(request: Request, skip: int = 0, limit: int = 50):
    """Admin endpoint to get all users"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    users = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for user in users:
        user["_id"] = str(user["_id"])
        if user.get("location"):
            try:
                user["location"] = decrypt_data(user["location"])
            except Exception:
                pass
        if user.get("bio"):
            try:
                user["bio"] = decrypt_data(user["bio"])
            except Exception:
                pass

    total = await db.users.count_documents({})
    return {"users": users, "total": total}


@router.get("/stats")
async def get_admin_stats(request: Request):
    """Admin endpoint to get platform statistics"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    total_users = await db.users.count_documents({})
    verified_users = await db.users.count_documents({"is_verified": True})
    total_posts = await db.posts.count_documents({})
    total_messages = await db.messages.count_documents({})
    total_connections = await db.network_connections.count_documents({})
    pending_requests = await db.network_requests.count_documents({"status": "pending"})
    total_invites = await db.invites.count_documents({})
    used_invites = await db.invites.count_documents({"used": True})

    week_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    new_users_week = await db.users.count_documents({"created_at": {"$gte": week_ago}})
    new_posts_week = await db.posts.count_documents({"created_at": {"$gte": week_ago}})

    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "total_posts": total_posts,
        "total_messages": total_messages,
        "total_connections": total_connections,
        "pending_requests": pending_requests,
        "total_invites": total_invites,
        "used_invites": used_invites,
        "new_users_week": new_users_week,
        "new_posts_week": new_posts_week,
    }


@router.get("/posts")
async def get_admin_posts(request: Request, skip: int = 0, limit: int = 50):
    """Admin endpoint to get all posts"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    posts = await db.posts.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for post in posts:
        post["_id"] = str(post["_id"])
        if post.get("description"):
            try:
                post["description"] = decrypt_data(post["description"])
            except Exception:
                pass
        if post.get("comments"):
            for comment in post["comments"]:
                if comment.get("content"):
                    try:
                        comment["content"] = decrypt_data(comment["content"])
                    except Exception:
                        pass

    total = await db.posts.count_documents({})
    return {"posts": posts, "total": total}


@router.delete("/posts/{post_id}")
async def admin_delete_post(post_id: str, request: Request):
    """Admin endpoint to delete any post"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    await db.posts.delete_one({"_id": ObjectId(post_id)})

    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="deleted_post",
        target_type="post",
        target_id=post_id,
        target_name=post.get("title", "Unknown Post"),
        details=f"Post by {post.get('user_name', 'Unknown')} deleted"
    )

    return {"message": "Post deleted successfully"}


@router.put("/users/{user_id}/role")
async def update_user_role(user_id: str, data: UpdateUserRole, request: Request):
    """Admin endpoint to change user role"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if data.role not in ["admin", "user"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": data.role}})

    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="role_changed",
        target_type="user",
        target_id=user_id,
        target_name=target.get("name", "Unknown"),
        details=f"Role changed from {target.get('role', 'user')} to {data.role}"
    )

    return {"message": f"User role updated to {data.role}", "user_id": user_id, "role": data.role}


@router.delete("/users/{user_id}")
async def admin_delete_user(user_id: str, request: Request):
    """Admin endpoint to delete a user"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if user_id == admin_user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    target = await db.users.find_one({"_id": ObjectId(user_id)})
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    await db.users.delete_one({"_id": ObjectId(user_id)})
    await db.posts.delete_many({"user_id": user_id})
    await db.messages.delete_many({"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]})
    await db.network_connections.delete_many({"$or": [{"user_id": user_id}, {"connected_user_id": user_id}]})
    await db.network_requests.delete_many({"$or": [{"from_user_id": user_id}, {"to_user_id": user_id}]})
    await db.push_subscriptions.delete_many({"user_id": user_id})

    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="deleted_user",
        target_type="user",
        target_id=user_id,
        target_name=target.get("name", "Unknown"),
        details=f"User {target.get('email', '')} and all associated data deleted"
    )

    return {"message": "User and all associated data deleted"}



# ========================
# System Messages (Banner Announcements)
# ========================

@router.post("/system-messages")
async def create_system_message(request: Request):
    """Create a new system-wide announcement banner"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    data = await request.json()
    message = data.get("message", "").strip()
    message_type = data.get("type", "info")  # info, warning, success, urgent
    is_active = data.get("is_active", True)
    priority = data.get("priority", 0)  # Higher priority = shown first
    
    if not message:
        raise HTTPException(status_code=400, detail="Message content is required")
    
    if message_type not in ["info", "warning", "success", "urgent"]:
        message_type = "info"
    
    msg_doc = {
        "message": message,
        "type": message_type,
        "is_active": is_active,
        "priority": priority,
        "created_by": admin_user["_id"],
        "created_by_name": admin_user.get("name", "Admin"),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.system_messages.insert_one(msg_doc)
    
    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="created_system_message",
        target_type="system_message",
        target_id=str(result.inserted_id),
        target_name=message[:50],
        details=f"Type: {message_type}, Active: {is_active}"
    )
    
    return {"id": str(result.inserted_id), "message": "System message created"}


@router.get("/system-messages")
async def get_all_system_messages(request: Request, skip: int = 0, limit: int = 50):
    """Get all system messages (admin view)"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    messages = await db.system_messages.find({}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    
    total = await db.system_messages.count_documents({})
    return {"messages": messages, "total": total}


@router.put("/system-messages/{message_id}")
async def update_system_message(message_id: str, request: Request):
    """Update a system message"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    data = await request.json()
    
    msg = await db.system_messages.find_one({"_id": ObjectId(message_id)})
    if not msg:
        raise HTTPException(status_code=404, detail="System message not found")
    
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if "message" in data:
        update_data["message"] = data["message"].strip()
    if "type" in data and data["type"] in ["info", "warning", "success", "urgent"]:
        update_data["type"] = data["type"]
    if "is_active" in data:
        update_data["is_active"] = bool(data["is_active"])
    if "priority" in data:
        update_data["priority"] = int(data["priority"])
    
    await db.system_messages.update_one(
        {"_id": ObjectId(message_id)},
        {"$set": update_data}
    )
    
    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="updated_system_message",
        target_type="system_message",
        target_id=message_id,
        target_name=msg.get("message", "")[:50],
        details=f"Updated fields: {list(update_data.keys())}"
    )
    
    return {"message": "System message updated"}


@router.delete("/system-messages/{message_id}")
async def delete_system_message(message_id: str, request: Request):
    """Delete a system message"""
    admin_user = await get_current_user(request)
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    msg = await db.system_messages.find_one({"_id": ObjectId(message_id)})
    if not msg:
        raise HTTPException(status_code=404, detail="System message not found")
    
    await db.system_messages.delete_one({"_id": ObjectId(message_id)})
    
    await log_admin_action(
        admin_id=admin_user["_id"],
        admin_name=admin_user.get("name", "Admin"),
        action="deleted_system_message",
        target_type="system_message",
        target_id=message_id,
        target_name=msg.get("message", "")[:50],
        details=""
    )
    
    return {"message": "System message deleted"}


# Public endpoint for active system messages
@router.get("/system-messages/active", tags=["Public"])
async def get_active_system_messages():
    """Get active system messages for display (no auth required)"""
    messages = await db.system_messages.find(
        {"is_active": True},
        {"_id": 1, "message": 1, "type": 1, "priority": 1}
    ).sort("priority", -1).limit(10).to_list(10)
    
    for msg in messages:
        msg["_id"] = str(msg["_id"])
    
    return {"messages": messages}
