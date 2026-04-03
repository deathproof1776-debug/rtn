"""
Object Storage Module for Rebel Trade Network
Provides persistent cloud storage for avatars, post images, and gallery media.
"""
import os
import uuid
import requests
import logging
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

STORAGE_URL = "https://integrations.emergentagent.com/objstore/api/v1/storage"
EMERGENT_KEY = os.environ.get("EMERGENT_LLM_KEY")
APP_NAME = "rebel-trade-network"

# Module-level storage key - initialized once and reused
_storage_key: Optional[str] = None

# Allowed file types for security
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/quicktime", "video/webm", "video/mpeg"}
ALLOWED_TYPES = ALLOWED_IMAGE_TYPES | ALLOWED_VIDEO_TYPES

# Max file sizes (in bytes)
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB

# MIME type mapping
MIME_TYPES = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "gif": "image/gif",
    "webp": "image/webp",
    "mp4": "video/mp4",
    "mov": "video/quicktime",
    "webm": "video/webm",
    "mpeg": "video/mpeg",
    "mpg": "video/mpeg"
}


def init_storage() -> str:
    """
    Initialize storage connection. Call once at startup.
    Returns the storage key for subsequent operations.
    """
    global _storage_key
    
    if _storage_key:
        return _storage_key
    
    if not EMERGENT_KEY:
        raise ValueError("EMERGENT_LLM_KEY environment variable not set")
    
    try:
        resp = requests.post(
            f"{STORAGE_URL}/init",
            json={"emergent_key": EMERGENT_KEY},
            timeout=30
        )
        resp.raise_for_status()
        _storage_key = resp.json()["storage_key"]
        logger.info("Object storage initialized successfully")
        return _storage_key
    except requests.RequestException as e:
        logger.error(f"Failed to initialize storage: {e}")
        raise


def get_storage_key() -> str:
    """Get the storage key, initializing if necessary."""
    if _storage_key is None:
        return init_storage()
    return _storage_key


def validate_file(content_type: str, size: int, file_category: str = "image") -> Tuple[bool, str]:
    """
    Validate file type and size for security.
    Returns (is_valid, error_message)
    """
    if file_category == "image":
        if content_type not in ALLOWED_IMAGE_TYPES:
            return False, f"Invalid image type. Allowed: JPEG, PNG, GIF, WebP"
        if size > MAX_IMAGE_SIZE:
            return False, f"Image too large. Maximum size: {MAX_IMAGE_SIZE // (1024*1024)}MB"
    elif file_category == "video":
        if content_type not in ALLOWED_VIDEO_TYPES:
            return False, f"Invalid video type. Allowed: MP4, MOV, WebM, MPEG"
        if size > MAX_VIDEO_SIZE:
            return False, f"Video too large. Maximum size: {MAX_VIDEO_SIZE // (1024*1024)}MB"
    elif file_category == "media":
        if content_type not in ALLOWED_TYPES:
            return False, f"Invalid file type. Allowed: images (JPEG, PNG, GIF, WebP) and videos (MP4, MOV, WebM)"
        max_size = MAX_VIDEO_SIZE if content_type in ALLOWED_VIDEO_TYPES else MAX_IMAGE_SIZE
        if size > max_size:
            return False, f"File too large. Maximum size: {max_size // (1024*1024)}MB"
    else:
        return False, "Unknown file category"
    
    return True, ""


def get_content_type(filename: str) -> str:
    """Get MIME type from filename extension."""
    if "." in filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        return MIME_TYPES.get(ext, "application/octet-stream")
    return "application/octet-stream"


def is_video(content_type: str) -> bool:
    """Check if content type is a video."""
    return content_type in ALLOWED_VIDEO_TYPES


def put_object(path: str, data: bytes, content_type: str) -> dict:
    """
    Upload a file to object storage.
    
    Args:
        path: Storage path (e.g., "rebel-trade-network/avatars/user123/file.jpg")
        data: File content as bytes
        content_type: MIME type of the file
        
    Returns:
        dict with path, size, etag
    """
    key = get_storage_key()
    
    try:
        resp = requests.put(
            f"{STORAGE_URL}/objects/{path}",
            headers={
                "X-Storage-Key": key,
                "Content-Type": content_type
            },
            data=data,
            timeout=120
        )
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        logger.error(f"Failed to upload object {path}: {e}")
        raise


def get_object(path: str) -> Tuple[bytes, str]:
    """
    Download a file from object storage.
    
    Args:
        path: Storage path
        
    Returns:
        Tuple of (content_bytes, content_type)
    """
    key = get_storage_key()
    
    try:
        resp = requests.get(
            f"{STORAGE_URL}/objects/{path}",
            headers={"X-Storage-Key": key},
            timeout=60
        )
        resp.raise_for_status()
        return resp.content, resp.headers.get("Content-Type", "application/octet-stream")
    except requests.RequestException as e:
        logger.error(f"Failed to get object {path}: {e}")
        raise


def generate_storage_path(user_id: str, category: str, filename: str) -> str:
    """
    Generate a secure storage path for a file.
    
    Args:
        user_id: The user's ID
        category: File category (avatars, posts, gallery)
        filename: Original filename
        
    Returns:
        Storage path with UUID to prevent collisions
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else "bin"
    unique_id = uuid.uuid4()
    return f"{APP_NAME}/{category}/{user_id}/{unique_id}.{ext}"
