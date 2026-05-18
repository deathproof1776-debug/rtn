"""
Posts routes: create posts, list feed, comments, likes.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from database import db, encrypt_data, safe_decrypt
from auth import get_current_user
from location import locations_match
from models import BarterPost, CommentCreate, normalize_items, get_item_names
from notifications import send_push_notification
from moderation_utils import get_blocked_user_ids

router = APIRouter()


@router.post("/posts", status_code=201)
async def create_post(post: BarterPost, request: Request):
    user = await get_current_user(request)
    
    # Validate required fields
    if not post.title or not post.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    if not post.description or not post.description.strip():
        raise HTTPException(status_code=400, detail="Description is required")
    
    post_doc = {
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "title": post.title.strip(),
        "description": encrypt_data(post.description.strip()),
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
async def get_posts(
    request: Request, 
    skip: int = 0, 
    limit: int = 20, 
    nearby_only: bool = False,
    network_only: bool = False,
    verified_only: bool = False,
    has_media: bool = False,
    category: str = None,
    time_range: str = None,
    sort_by: str = None,
    search: str = None
):
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

    user_location = safe_decrypt(user_doc.get("location"))
    blocked_ids = await get_blocked_user_ids(user["_id"])

    # Build query with filters
    query = {}
    if blocked_ids:
        query["user_id"] = {"$nin": list(blocked_ids)}
    if category and category != "all":
        query["category"] = category
    if network_only:
        # Network filter takes precedence; intersect with non-blocked
        allowed = network_user_ids - blocked_ids
        query["user_id"] = {"$in": list(allowed)}
    if has_media:
        query["images"] = {"$exists": True, "$ne": []}
    
    # Time range filter
    if time_range and time_range != "all":
        now = datetime.now(timezone.utc)
        if time_range == "today":
            start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
        elif time_range == "week":
            start_date = now - timedelta(days=7)
        elif time_range == "month":
            start_date = now - timedelta(days=30)
        else:
            start_date = None
        if start_date:
            query["created_at"] = {"$gte": start_date.isoformat()}
    
    # Search filter
    if search and search.strip():
        search_term = search.strip()
        query["$or"] = [
            {"title": {"$regex": search_term, "$options": "i"}},
            {"user_name": {"$regex": search_term, "$options": "i"}}
        ]

    # Determine sort order
    sort_field = "created_at"
    sort_direction = -1
    if sort_by == "popular":
        # Will sort by likes count in memory
        pass
    elif sort_by == "commented":
        # Will sort by comments count in memory
        pass

    posts = await db.posts.find(
        query,
        {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1,
         "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1, "likes": 1, "comments": 1}
    ).sort(sort_field, sort_direction).skip(skip).limit(100 if nearby_only else limit * 3).to_list(100 if nearby_only else limit * 3)

    # Get user locations and verification status
    user_ids = list(set([p["user_id"] for p in posts]))
    users_map = {}
    if user_ids:
        users_cursor = db.users.find({"_id": {"$in": [ObjectId(uid) for uid in user_ids]}}, {"_id": 1, "location": 1, "is_verified": 1, "is_trusted_trader": 1})
        async for u in users_cursor:
            uid = str(u["_id"])
            users_map[uid] = {
                "location": safe_decrypt(u.get("location")),
                "is_verified": u.get("is_verified", False),
                "is_trusted_trader": u.get("is_trusted_trader", False)
            }

    result_posts = []
    for post in posts:
        post["_id"] = str(post["_id"])
        post["description"] = safe_decrypt(post.get("description"))
        # Decrypt comment content
        for comment in post.get("comments") or []:
            comment["content"] = safe_decrypt(comment.get("content"))

        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False, "is_trusted_trader": False})
        poster_location = user_data["location"]
        post["user_location"] = poster_location
        post["is_nearby"] = locations_match(user_location, poster_location) if user_location else False
        post["is_verified"] = user_data["is_verified"]
        post["is_trusted_trader"] = user_data.get("is_trusted_trader", False)
        post["is_network"] = post["user_id"] in network_user_ids

        feed_score = 0
        if post["is_network"]:
            feed_score += 200
        if post.get("is_nearby"):
            feed_score += 100
        post["feed_score"] = feed_score

        # Apply filters
        if verified_only and not post["is_verified"]:
            continue
        if nearby_only and not post["is_nearby"]:
            continue
        
        result_posts.append(post)

    # Apply sorting based on sort_by parameter
    if sort_by == "popular":
        result_posts.sort(key=lambda x: len(x.get("likes", [])), reverse=True)
    elif sort_by == "commented":
        result_posts.sort(key=lambda x: len(x.get("comments", [])), reverse=True)
    else:
        # Default: sort by feed_score then created_at
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

    user_location = safe_decrypt(user_doc.get("location"))
    blocked_ids = await get_blocked_user_ids(user["_id"])

    user_wants = (get_item_names(user_doc.get("goods_wanted", [])) +
                  get_item_names(user_doc.get("services_wanted", [])))
    user_offerings = (get_item_names(user_doc.get("goods_offering", [])) +
                      get_item_names(user_doc.get("services_offering", [])))

    query = {"user_id": {"$ne": user["_id"]}}
    if blocked_ids:
        query["user_id"] = {"$nin": list(blocked_ids) + [user["_id"]]}
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
            users_map[uid] = {
                "location": safe_decrypt(u.get("location")),
                "is_verified": u.get("is_verified", False),
            }

    for post in posts:
        post["_id"] = str(post["_id"])
        post["description"] = safe_decrypt(post.get("description"))

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
    user = await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)}, {"comments": 1})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    blocked_ids = await get_blocked_user_ids(user["_id"])

    comments = post.get("comments", [])
    visible = []
    for comment in comments:
        if comment.get("user_id") in blocked_ids:
            continue
        comment["content"] = safe_decrypt(comment.get("content"))
        if "parent_id" not in comment:
            comment["parent_id"] = None
        if "replies" not in comment:
            comment["replies"] = []
        visible.append(comment)

    return visible


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


@router.put("/posts/{post_id}")
async def update_post(post_id: str, request: Request):
    """Update a post - user can only edit their own posts"""
    user = await get_current_user(request)
    data = await request.json()
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Only owner can edit
    if post.get("user_id") != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this post")
    
    # Build update document
    update_data = {"updated_at": datetime.now(timezone.utc).isoformat()}
    
    if "title" in data and data["title"].strip():
        update_data["title"] = data["title"].strip()
    if "description" in data:
        update_data["description"] = encrypt_data(data["description"].strip()) if data["description"] else ""
    if "category" in data:
        update_data["category"] = data["category"]
    if "offering" in data:
        update_data["offering"] = normalize_items(data["offering"])
    if "looking_for" in data:
        update_data["looking_for"] = normalize_items(data["looking_for"])
    if "images" in data:
        update_data["images"] = data["images"]
    
    await db.posts.update_one({"_id": ObjectId(post_id)}, {"$set": update_data})
    
    return {"message": "Post updated successfully"}


@router.put("/posts/{post_id}/comments/{comment_id}")
async def update_comment(post_id: str, comment_id: str, request: Request):
    """Update a comment - user can only edit their own comments"""
    user = await get_current_user(request)
    data = await request.json()
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Find the comment
    comment_to_update = None
    for comment in post.get("comments", []):
        if comment.get("id") == comment_id:
            comment_to_update = comment
            break
    
    if not comment_to_update:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Only owner can edit
    if comment_to_update["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this comment")
    
    new_content = data.get("content", "").strip()
    if not new_content:
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    # Update the comment in the array
    await db.posts.update_one(
        {"_id": ObjectId(post_id), "comments.id": comment_id},
        {"$set": {
            "comments.$.content": encrypt_data(new_content),
            "comments.$.updated_at": datetime.now(timezone.utc).isoformat()
        }}
    )
    
    return {
        "message": "Comment updated successfully",
        "content": new_content,
        "updated_at": datetime.now(timezone.utc).isoformat()
    }


@router.delete("/posts/{post_id}")
async def delete_post(post_id: str, request: Request):
    """Delete a post - user can delete their own, admin can delete any"""
    user = await get_current_user(request)
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check authorization - user can delete their own post, admin can delete any
    is_owner = post.get("user_id") == user["_id"]
    is_admin = user.get("role") == "admin"
    
    if not is_owner and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    
    # Delete the post
    await db.posts.delete_one({"_id": ObjectId(post_id)})
    
    return {"message": "Post deleted successfully"}

