"""
Posts routes: create posts, list feed, comments, likes.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from models import BarterPost, CommentCreate, normalize_items, get_item_names
from notifications import send_push_notification

router = APIRouter()


def normalize_location(location: str) -> str:
    """Normalize location string for comparison"""
    if not location:
        return ""
    return location.lower().strip()


def locations_match(loc1: str, loc2: str) -> bool:
    """Check if two locations match (same city/state/region)"""
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


@router.post("/posts", status_code=201)
async def create_post(post: BarterPost, request: Request):
    user = await get_current_user(request)
    post_doc = {
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "title": post.title,
        "description": encrypt_data(post.description),
        "category": post.category,
        "offering": normalize_items(post.offering),
        "looking_for": normalize_items(post.looking_for),
        "images": post.images,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "likes": [],
        "comments": []
    }
    result = await db.posts.insert_one(post_doc)
    return {"id": str(result.inserted_id), "message": "Post created successfully"}


@router.get("/posts")
async def get_posts(request: Request, skip: int = 0, limit: int = 20, nearby_only: bool = False):
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})

    # Get user's trade network connections
    network_connections = await db.network_connections.find({
        "$or": [
            {"user_id": user["_id"]},
            {"connected_user_id": user["_id"]}
        ]
    }).to_list(500)

    network_user_ids = set()
    for conn in network_connections:
        if conn["user_id"] == user["_id"]:
            network_user_ids.add(conn["connected_user_id"])
        else:
            network_user_ids.add(conn["user_id"])

    # Decrypt user's location
    user_location = ""
    if user_doc.get("location"):
        try:
            user_location = decrypt_data(user_doc["location"])
        except Exception:
            user_location = user_doc.get("location", "")

    posts = await db.posts.find(
        {},
        {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1,
         "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1, "likes": 1, "comments": 1}
    ).sort("created_at", -1).skip(skip).limit(100 if nearby_only else limit * 3).to_list(100 if nearby_only else limit * 3)

    # Get user locations and verification status
    user_ids = list(set([p["user_id"] for p in posts]))
    users_map = {}
    if user_ids:
        users_cursor = db.users.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}, {"_id": 1, "location": 1, "is_verified": 1})
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
        if post.get("description"):
            try:
                post["description"] = decrypt_data(post["description"])
            except Exception:
                pass
        # Decrypt comment content
        if post.get("comments"):
            for comment in post["comments"]:
                if comment.get("content"):
                    try:
                        comment["content"] = decrypt_data(comment["content"])
                    except Exception:
                        pass

        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False})
        poster_location = user_data["location"]
        post["user_location"] = poster_location
        post["is_nearby"] = locations_match(user_location, poster_location) if user_location else False
        post["is_verified"] = user_data["is_verified"]
        post["is_network"] = post["user_id"] in network_user_ids

        feed_score = 0
        if post["is_network"]:
            feed_score += 200
        if post.get("is_nearby"):
            feed_score += 100
        post["feed_score"] = feed_score

        if nearby_only:
            if post["is_nearby"]:
                result_posts.append(post)
        else:
            result_posts.append(post)

    result_posts.sort(key=lambda x: (-x.get("feed_score", 0), x.get("created_at", "")), reverse=False)
    result_posts.sort(key=lambda x: -x.get("feed_score", 0))

    return result_posts[:limit]


@router.get("/posts/matches")
async def get_matched_posts(request: Request):
    """Get posts that match user's wants with others' offerings"""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})

    network_connections = await db.network_connections.find({
        "$or": [
            {"user_id": user["_id"]},
            {"connected_user_id": user["_id"]}
        ]
    }).to_list(500)

    network_user_ids = set()
    for conn in network_connections:
        if conn["user_id"] == user["_id"]:
            network_user_ids.add(conn["connected_user_id"])
        else:
            network_user_ids.add(conn["user_id"])

    user_location = ""
    if user_doc.get("location"):
        try:
            user_location = decrypt_data(user_doc["location"])
        except Exception:
            user_location = user_doc.get("location", "")

    user_wants = (get_item_names(user_doc.get("goods_wanted", [])) +
                  get_item_names(user_doc.get("services_wanted", [])))
    user_offerings = (get_item_names(user_doc.get("goods_offering", [])) +
                      get_item_names(user_doc.get("services_offering", [])))

    query = {"user_id": {"$ne": user["_id"]}}
    if user_wants or user_offerings:
        or_conditions = []
        if user_wants:
            or_conditions.append({"$or": [
                {"offering": {"$in": user_wants}},
                {"offering.name": {"$in": user_wants}}
            ]})
        if user_offerings:
            or_conditions.append({"$or": [
                {"looking_for": {"$in": user_offerings}},
                {"looking_for.name": {"$in": user_offerings}}
            ]})
        if or_conditions:
            query["$or"] = or_conditions

    posts = await db.posts.find(
        query,
        {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1,
         "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1}
    ).sort("created_at", -1).limit(50).to_list(50)

    user_ids = list(set([p["user_id"] for p in posts]))
    users_map = {}
    if user_ids:
        users_cursor = db.users.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}, {"_id": 1, "location": 1, "is_verified": 1})
        async for u in users_cursor:
            uid = str(u["_id"])
            loc = ""
            if u.get("location"):
                try:
                    loc = decrypt_data(u["location"])
                except Exception:
                    loc = u.get("location", "")
            users_map[uid] = {"location": loc, "is_verified": u.get("is_verified", False)}

    for post in posts:
        post["_id"] = str(post["_id"])
        if post.get("description"):
            try:
                post["description"] = decrypt_data(post["description"])
            except Exception:
                pass

        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False})
        poster_location = user_data["location"]
        post["user_location"] = poster_location
        post["is_nearby"] = locations_match(user_location, poster_location) if user_location else False
        post["is_verified"] = user_data["is_verified"]
        post["is_network"] = post["user_id"] in network_user_ids

        score = 0
        if post["is_network"]:
            score += 200
        if post.get("is_nearby"):
            score += 100
        post_offerings = get_item_names(post.get("offering", []))
        post_looking = get_item_names(post.get("looking_for", []))
        for item in post_offerings:
            if item in user_wants:
                score += 10
        for item in post_looking:
            if item in user_offerings:
                score += 10
        post["match_score"] = score

    posts.sort(key=lambda x: (-x.get("match_score", 0), x.get("created_at", "")), reverse=False)
    posts.sort(key=lambda x: -x.get("match_score", 0))

    return posts[:20]


@router.post("/posts/{post_id}/like")
async def like_post(post_id: str, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if user["_id"] in post.get("likes", []):
        await db.posts.update_one({"_id": ObjectId(post_id)}, {"$pull": {"likes": user["_id"]}})
        return {"message": "Post unliked"}
    else:
        await db.posts.update_one({"_id": ObjectId(post_id)}, {"$addToSet": {"likes": user["_id"]}})

        if post["user_id"] != user["_id"]:
            background_tasks.add_task(
                send_push_notification,
                user_id=post["user_id"],
                title=f"{user.get('name', 'Someone')} liked your post",
                body=post.get("title", "Your barter post")[:50],
                data={"type": "like", "post_id": post_id, "url": "/"}
            )

        return {"message": "Post liked"}


@router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: str, comment: CommentCreate, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)

    if not comment.content or not comment.content.strip():
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")

    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    parent_user_id = None
    if comment.parent_id:
        parent_comment = None
        for c in post.get("comments", []):
            if c.get("id") == comment.parent_id:
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
        "content": encrypt_data(comment.content),
        "parent_id": comment.parent_id,
        "replies": [],
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment_doc}}
    )

    if comment.parent_id:
        await db.posts.update_one(
            {"_id": ObjectId(post_id), "comments.id": comment.parent_id},
            {"$push": {"comments.$.replies": comment_doc["id"]}}
        )

    if post["user_id"] != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=post["user_id"],
            title=f"{user.get('name', 'Someone')} commented on your post",
            body=comment.content[:100] + ("..." if len(comment.content) > 100 else ""),
            data={"type": "comment", "post_id": post_id, "url": "/"}
        )

    if comment.parent_id and parent_user_id and parent_user_id != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=parent_user_id,
            title=f"{user.get('name', 'Someone')} replied to your comment",
            body=comment.content[:100] + ("..." if len(comment.content) > 100 else ""),
            data={"type": "reply", "post_id": post_id, "url": "/"}
        )

    return {
        "id": comment_doc["id"],
        "user_id": comment_doc["user_id"],
        "user_name": comment_doc["user_name"],
        "user_avatar": comment_doc["user_avatar"],
        "content": comment.content,
        "parent_id": comment.parent_id,
        "replies": [],
        "created_at": comment_doc["created_at"]
    }


@router.get("/posts/{post_id}/comments")
async def get_comments(post_id: str, request: Request):
    await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)}, {"comments": 1})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comments = post.get("comments", [])
    for comment in comments:
        if comment.get("content"):
            try:
                comment["content"] = decrypt_data(comment["content"])
            except Exception:
                pass
        if "parent_id" not in comment:
            comment["parent_id"] = None
        if "replies" not in comment:
            comment["replies"] = []

    return comments


@router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, request: Request):
    user = await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment_to_delete = None
    for comment in post.get("comments", []):
        if comment.get("id") == comment_id:
            comment_to_delete = comment
            break

    if not comment_to_delete:
        raise HTTPException(status_code=404, detail="Comment not found")

    if comment_to_delete["user_id"] != user["_id"] and post["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")

    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"id": comment_id}}}
    )

    return {"message": "Comment deleted"}
