"""
Community Board routes: general discussion posts for homesteading/off-grid community.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone
from typing import List, Optional

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from notifications import send_push_notification

router = APIRouter(prefix="/community")

# Community post categories/topics
COMMUNITY_TOPICS = [
    {"id": "homesteading", "name": "Homesteading", "icon": "house"},
    {"id": "off-grid", "name": "Off-Grid Living", "icon": "lightning"},
    {"id": "prepping", "name": "Prepping & Preparedness", "icon": "shield"},
    {"id": "diy", "name": "DIY & Building", "icon": "hammer"},
    {"id": "gardening", "name": "Gardening & Farming", "icon": "plant"},
    {"id": "livestock", "name": "Livestock & Animals", "icon": "cow"},
    {"id": "food", "name": "Food Preservation", "icon": "jar"},
    {"id": "energy", "name": "Alternative Energy", "icon": "sun"},
    {"id": "water", "name": "Water Systems", "icon": "drop"},
    {"id": "security", "name": "Security & Defense", "icon": "lock"},
    {"id": "health", "name": "Natural Health", "icon": "heart"},
    {"id": "finance", "name": "Financial Independence", "icon": "currency"},
    {"id": "community", "name": "Community Building", "icon": "users"},
    {"id": "news", "name": "News & Updates", "icon": "newspaper"},
    {"id": "general", "name": "General Discussion", "icon": "chat"}
]


def normalize_location(location: str) -> str:
    if not location:
        return ""
    return location.lower().strip()


def locations_match(loc1: str, loc2: str) -> bool:
    if not loc1 or not loc2:
        return False
    norm1 = normalize_location(loc1)
    norm2 = normalize_location(loc2)
    if not norm1 or not norm2:
        return False
    if norm1 == norm2:
        return True
    if norm1 in norm2 or norm2 in norm1:
        return True
    parts1 = [p.strip() for p in norm1.split(',')]
    parts2 = [p.strip() for p in norm2.split(',')]
    for p1 in parts1:
        for p2 in parts2:
            if p1 and p2 and (p1 == p2 or p1 in p2 or p2 in p1):
                return True
    return False


@router.get("/topics")
async def get_community_topics():
    """Get all available community topics/categories"""
    return {"topics": COMMUNITY_TOPICS}


@router.post("", status_code=201)
async def create_community_post(request: Request):
    """Create a new community post"""
    user = await get_current_user(request)
    data = await request.json()
    
    title = data.get("title", "").strip()
    content = data.get("content", "").strip()
    topic = data.get("topic", "general")
    images = data.get("images", [])
    
    if not title:
        raise HTTPException(status_code=400, detail="Title is required")
    if not content:
        raise HTTPException(status_code=400, detail="Content is required")
    
    # Validate topic
    valid_topics = [t["id"] for t in COMMUNITY_TOPICS]
    if topic not in valid_topics:
        topic = "general"
    
    post_doc = {
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "title": title,
        "content": encrypt_data(content),
        "topic": topic,
        "images": images[:5],  # Limit to 5 images
        "likes": [],
        "comments": [],
        "is_pinned": False,
        "is_deleted": False,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat()
    }
    
    result = await db.community_posts.insert_one(post_doc)
    return {"id": str(result.inserted_id), "message": "Post created successfully"}


@router.get("")
async def get_community_posts(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    topic: Optional[str] = None,
    nearby_only: bool = False,
    network_only: bool = False,
    verified_only: bool = False
):
    """Get community posts with optional filters"""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    
    # Build query
    query = {"is_deleted": False}
    if topic and topic != "all":
        query["topic"] = topic
    
    # Get user's network connections
    network_user_ids = set()
    if network_only:
        connections = await db.network_connections.find({
            "$or": [
                {"user_id": user["_id"]},
                {"connected_user_id": user["_id"]}
            ]
        }).to_list(500)
        for conn in connections:
            if conn["user_id"] == user["_id"]:
                network_user_ids.add(conn["connected_user_id"])
            else:
                network_user_ids.add(conn["user_id"])
        query["user_id"] = {"$in": list(network_user_ids)}
    
    # Decrypt user's location for nearby filter
    user_location = ""
    if user_doc.get("location"):
        try:
            user_location = decrypt_data(user_doc["location"])
        except Exception:
            user_location = user_doc.get("location", "")
    
    # Fetch posts
    posts = await db.community_posts.find(
        query,
        {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, 
         "content": 1, "topic": 1, "images": 1, "likes": 1, "comments": 1,
         "is_pinned": 1, "created_at": 1}
    ).sort([("is_pinned", -1), ("created_at", -1)]).skip(skip).limit(limit * 2).to_list(limit * 2)
    
    # Get user info for posts
    user_ids = list(set([p["user_id"] for p in posts]))
    users_map = {}
    if user_ids:
        users_cursor = db.users.find(
            {"_id": {"$in": [ObjectId(uid) for uid in user_ids]}},
            {"_id": 1, "location": 1, "is_verified": 1}
        )
        async for u in users_cursor:
            uid = str(u["_id"])
            loc = ""
            if u.get("location"):
                try:
                    loc = decrypt_data(u["location"])
                except Exception:
                    loc = u.get("location", "")
            users_map[uid] = {"location": loc, "is_verified": u.get("is_verified", False)}
    
    result_posts = []
    for post in posts:
        post["_id"] = str(post["_id"])
        
        # Decrypt content
        if post.get("content"):
            try:
                post["content"] = decrypt_data(post["content"])
            except Exception:
                pass
        
        # Decrypt comments
        if post.get("comments"):
            for comment in post["comments"]:
                if comment.get("content"):
                    try:
                        comment["content"] = decrypt_data(comment["content"])
                    except Exception:
                        pass
        
        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False})
        post["user_location"] = user_data["location"]
        post["is_verified"] = user_data["is_verified"]
        post["is_nearby"] = locations_match(user_location, user_data["location"]) if user_location else False
        post["is_network"] = post["user_id"] in network_user_ids
        
        # Apply filters
        if verified_only and not post["is_verified"]:
            continue
        if nearby_only and not post["is_nearby"]:
            continue
        
        result_posts.append(post)
    
    return result_posts[:limit]


@router.get("/{post_id}")
async def get_community_post(post_id: str, request: Request):
    """Get a single community post"""
    await get_current_user(request)
    
    post = await db.community_posts.find_one({"_id": ObjectId(post_id), "is_deleted": False})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post["_id"] = str(post["_id"])
    if post.get("content"):
        try:
            post["content"] = decrypt_data(post["content"])
        except Exception:
            pass
    
    if post.get("comments"):
        for comment in post["comments"]:
            if comment.get("content"):
                try:
                    comment["content"] = decrypt_data(comment["content"])
                except Exception:
                    pass
    
    return post


@router.post("/{post_id}/like")
async def like_community_post(post_id: str, request: Request, background_tasks: BackgroundTasks):
    """Like or unlike a community post"""
    user = await get_current_user(request)
    
    post = await db.community_posts.find_one({"_id": ObjectId(post_id), "is_deleted": False})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if user["_id"] in post.get("likes", []):
        await db.community_posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$pull": {"likes": user["_id"]}}
        )
        return {"message": "Post unliked", "liked": False}
    else:
        await db.community_posts.update_one(
            {"_id": ObjectId(post_id)},
            {"$addToSet": {"likes": user["_id"]}}
        )
        
        if post["user_id"] != user["_id"]:
            background_tasks.add_task(
                send_push_notification,
                user_id=post["user_id"],
                title=f"{user.get('name', 'Someone')} liked your post",
                body=post.get("title", "")[:50],
                data={"type": "community_like", "post_id": post_id, "url": "/community"}
            )
        
        return {"message": "Post liked", "liked": True}


@router.post("/{post_id}/comments", status_code=201)
async def create_community_comment(post_id: str, request: Request, background_tasks: BackgroundTasks):
    """Add a comment to a community post"""
    user = await get_current_user(request)
    data = await request.json()
    
    content = data.get("content", "").strip()
    parent_id = data.get("parent_id")
    
    if not content:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    post = await db.community_posts.find_one({"_id": ObjectId(post_id), "is_deleted": False})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Validate parent comment if replying
    parent_user_id = None
    if parent_id:
        parent_comment = None
        for c in post.get("comments", []):
            if c.get("id") == parent_id:
                parent_comment = c
                break
        if not parent_comment:
            raise HTTPException(status_code=404, detail="Parent comment not found")
        parent_user_id = parent_comment.get("user_id")
    
    comment_doc = {
        "id": str(ObjectId()),
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "content": encrypt_data(content),
        "parent_id": parent_id,
        "replies": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.community_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment_doc}}
    )
    
    # Update parent's replies array
    if parent_id:
        await db.community_posts.update_one(
            {"_id": ObjectId(post_id), "comments.id": parent_id},
            {"$push": {"comments.$.replies": comment_doc["id"]}}
        )
    
    # Send notifications
    if post["user_id"] != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=post["user_id"],
            title=f"{user.get('name', 'Someone')} commented on your post",
            body=content[:100],
            data={"type": "community_comment", "post_id": post_id, "url": "/community"}
        )
    
    if parent_id and parent_user_id and parent_user_id != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=parent_user_id,
            title=f"{user.get('name', 'Someone')} replied to your comment",
            body=content[:100],
            data={"type": "community_reply", "post_id": post_id, "url": "/community"}
        )
    
    return {
        "id": comment_doc["id"],
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "content": content,
        "parent_id": parent_id,
        "replies": [],
        "created_at": comment_doc["created_at"]
    }


@router.delete("/{post_id}")
async def delete_community_post(post_id: str, request: Request):
    """Delete a community post (soft delete)"""
    user = await get_current_user(request)
    
    post = await db.community_posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only post owner or admin can delete
    if post["user_id"] != user["_id"] and user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.community_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$set": {"is_deleted": True}}
    )
    
    return {"message": "Post deleted"}


@router.delete("/{post_id}/comments/{comment_id}")
async def delete_community_comment(post_id: str, comment_id: str, request: Request):
    """Delete a comment from a community post"""
    user = await get_current_user(request)
    
    post = await db.community_posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_to_delete = None
    for comment in post.get("comments", []):
        if comment.get("id") == comment_id:
            comment_to_delete = comment
            break
    
    if not comment_to_delete:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only comment owner, post owner, or admin can delete
    if (comment_to_delete["user_id"] != user["_id"] and 
        post["user_id"] != user["_id"] and 
        user.get("role") != "admin"):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    await db.community_posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"id": comment_id}}}
    )
    
    return {"message": "Comment deleted"}
