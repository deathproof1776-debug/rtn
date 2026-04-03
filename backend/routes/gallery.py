"""
Gallery routes: upload, view, like, comment on photos/videos.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone
import uuid

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from models import GalleryCommentCreate
from notifications import send_push_notification
from storage import put_object, generate_storage_path, validate_file, get_content_type, is_video

router = APIRouter(prefix="/gallery")


@router.post("/upload")
async def upload_gallery_item(
    request: Request,
    file: UploadFile = File(...),
    caption: str = Form(default="")
):
    """Upload a photo or video to user's gallery"""
    user = await get_current_user(request)
    user_id = user["_id"]

    content = await file.read()
    content_type = file.content_type or get_content_type(file.filename)

    is_valid, error_msg = validate_file(content_type, len(content), "media")
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    storage_path = generate_storage_path(user_id, "gallery", file.filename)

    try:
        result = put_object(storage_path, content, content_type)

        gallery_id = str(uuid.uuid4())
        gallery_doc = {
            "id": gallery_id,
            "user_id": user_id,
            "user_name": user.get("name", "Unknown"),
            "storage_path": result["path"],
            "original_filename": file.filename,
            "content_type": content_type,
            "is_video": is_video(content_type),
            "caption": caption,
            "likes": [],
            "comments": [],
            "like_count": 0,
            "comment_count": 0,
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.gallery.insert_one(gallery_doc)

        return {
            "id": gallery_id,
            "url": f"/api/files/{result['path']}",
            "is_video": is_video(content_type)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload: {str(e)}")


@router.get("")
async def get_gallery(request: Request, user_id: str = None, skip: int = 0, limit: int = 20):
    """Get gallery items for a user (or all if user_id not provided)"""
    await get_current_user(request)

    query = {"is_deleted": False}
    if user_id:
        query["user_id"] = user_id

    items = await db.gallery.find(
        query,
        {"_id": 0}
    ).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    for item in items:
        item["url"] = f"/api/files/{item['storage_path']}"

    return items


@router.get("/{item_id}")
async def get_gallery_item(item_id: str, request: Request):
    """Get a single gallery item"""
    await get_current_user(request)

    item = await db.gallery.find_one({"id": item_id, "is_deleted": False}, {"_id": 0})
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")

    item["url"] = f"/api/files/{item['storage_path']}"

    # Decrypt comments
    for comment in item.get("comments", []):
        if comment.get("content"):
            try:
                comment["content"] = decrypt_data(comment["content"])
            except Exception:
                pass

    return item


@router.post("/{item_id}/like")
async def like_gallery_item(item_id: str, request: Request, background_tasks: BackgroundTasks):
    """Like or unlike a gallery item"""
    user = await get_current_user(request)

    item = await db.gallery.find_one({"id": item_id, "is_deleted": False})
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")

    if user["_id"] in item.get("likes", []):
        await db.gallery.update_one(
            {"id": item_id},
            {
                "$pull": {"likes": user["_id"]},
                "$inc": {"like_count": -1}
            }
        )
        return {"message": "Unliked", "liked": False}
    else:
        await db.gallery.update_one(
            {"id": item_id},
            {
                "$addToSet": {"likes": user["_id"]},
                "$inc": {"like_count": 1}
            }
        )

        if item["user_id"] != user["_id"]:
            background_tasks.add_task(
                send_push_notification,
                user_id=item["user_id"],
                title=f"{user.get('name', 'Someone')} liked your photo",
                body=item.get("caption", "")[:50] or "Your gallery item",
                data={"type": "gallery_like", "item_id": item_id, "url": "/"}
            )

        return {"message": "Liked", "liked": True}


@router.post("/{item_id}/comment")
async def comment_on_gallery_item(item_id: str, comment: GalleryCommentCreate, request: Request, background_tasks: BackgroundTasks):
    """Add a comment to a gallery item"""
    user = await get_current_user(request)

    if not comment.content or not comment.content.strip():
        raise HTTPException(status_code=400, detail="Comment cannot be empty")

    item = await db.gallery.find_one({"id": item_id, "is_deleted": False})
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")

    # Validate parent_id if provided
    parent_user_id = None
    if comment.parent_id:
        parent_comment = None
        for c in item.get("comments", []):
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

    await db.gallery.update_one(
        {"id": item_id},
        {
            "$push": {"comments": comment_doc},
            "$inc": {"comment_count": 1}
        }
    )

    # Update parent's replies array if this is a reply
    if comment.parent_id:
        await db.gallery.update_one(
            {"id": item_id, "comments.id": comment.parent_id},
            {"$push": {"comments.$.replies": comment_doc["id"]}}
        )

    if item["user_id"] != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=item["user_id"],
            title=f"{user.get('name', 'Someone')} commented on your photo",
            body=comment.content[:100],
            data={"type": "gallery_comment", "item_id": item_id, "url": "/"}
        )

    # Notify parent comment author if replying
    if comment.parent_id and parent_user_id and parent_user_id != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=parent_user_id,
            title=f"{user.get('name', 'Someone')} replied to your comment",
            body=comment.content[:100],
            data={"type": "gallery_reply", "item_id": item_id, "url": "/"}
        )

    return {
        "id": comment_doc["id"],
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "content": comment.content,
        "parent_id": comment.parent_id,
        "replies": [],
        "created_at": comment_doc["created_at"]
    }


@router.delete("/{item_id}")
async def delete_gallery_item(item_id: str, request: Request):
    """Soft delete a gallery item"""
    user = await get_current_user(request)

    item = await db.gallery.find_one({"id": item_id, "is_deleted": False})
    if not item:
        raise HTTPException(status_code=404, detail="Gallery item not found")

    if item["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.gallery.update_one(
        {"id": item_id},
        {"$set": {"is_deleted": True}}
    )

    return {"message": "Gallery item deleted"}
