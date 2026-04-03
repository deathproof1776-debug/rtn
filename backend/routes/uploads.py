"""
File upload routes: upload and retrieve files from object storage.
"""
from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form, Response, Query
from fastapi.responses import FileResponse
from pathlib import Path
from typing import Optional
from datetime import datetime, timezone
import uuid
import logging

from database import db
from auth import get_current_user
from storage import (
    put_object, get_object, generate_storage_path,
    validate_file, get_content_type, is_video
)

logger = logging.getLogger(__name__)
router = APIRouter()
ROOT_DIR = Path(__file__).parent.parent


@router.post("/upload")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(default="general")
):
    """Upload a file to persistent object storage."""
    user = await get_current_user(request)
    user_id = user["_id"]

    content = await file.read()
    content_type = file.content_type or get_content_type(file.filename)

    file_category = "video" if is_video(content_type) else "image"

    is_valid, error_msg = validate_file(content_type, len(content), file_category)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    storage_path = generate_storage_path(user_id, category, file.filename)

    try:
        result = put_object(storage_path, content, content_type)

        file_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "storage_path": result["path"],
            "original_filename": file.filename,
            "content_type": content_type,
            "size": result.get("size", len(content)),
            "category": category,
            "is_video": is_video(content_type),
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.files.insert_one(file_doc)

        return {
            "url": f"/api/files/{result['path']}",
            "path": result["path"],
            "filename": file.filename,
            "content_type": content_type,
            "is_video": is_video(content_type)
        }
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file")


@router.get("/files/{path:path}")
async def get_file(
    path: str,
    request: Request,
    auth: Optional[str] = Query(None)
):
    """Retrieve a file from object storage."""
    # Check files collection
    file_record = await db.files.find_one({"storage_path": path, "is_deleted": False})

    # Also check gallery collection if not found
    if not file_record:
        gallery_record = await db.gallery.find_one({"storage_path": path, "is_deleted": False})
        if gallery_record:
            file_record = {
                "storage_path": gallery_record["storage_path"],
                "content_type": gallery_record.get("content_type", "application/octet-stream")
            }

    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")

    try:
        data, content_type = get_object(path)
        return Response(
            content=data,
            media_type=file_record.get("content_type", content_type)
        )
    except Exception as e:
        logger.error(f"Failed to retrieve file {path}: {e}")
        raise HTTPException(status_code=404, detail="File not found")


@router.get("/uploads/{filename}")
async def get_legacy_upload(filename: str):
    """Legacy endpoint for backwards compatibility with local uploads."""
    filepath = ROOT_DIR / "uploads" / filename
    if filepath.exists():
        return FileResponse(filepath)
    raise HTTPException(status_code=404, detail="File not found")
