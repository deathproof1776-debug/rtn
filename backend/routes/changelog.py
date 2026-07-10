"""
Changelog routes: one-time per-user update notices.
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from bson import ObjectId
from datetime import datetime, timezone

from database import db
from auth import get_current_user, require_admin

router = APIRouter(prefix="/changelog")
admin_router = APIRouter(prefix="/admin/changelog")


@router.get("/latest")
async def get_latest_changelog(request: Request):
    """Return the latest active changelog the current user has NOT yet seen."""
    user = await get_current_user(request)
    latest = await db.changelogs.find_one({"active": True}, sort=[("created_at", -1)])
    if not latest:
        return {"changelog": None}

    changelog_id = str(latest["_id"])
    user_doc = await db.users.find_one(
        {"_id": ObjectId(user["_id"])},
        {"changelog_seen": 1}
    )
    seen = user_doc.get("changelog_seen", []) if user_doc else []
    if changelog_id in seen:
        return {"changelog": None}

    latest["_id"] = changelog_id
    return {"changelog": latest}


@router.post("/{changelog_id}/ack")
async def ack_changelog(changelog_id: str, request: Request):
    """Mark a changelog as seen for the current user."""
    user = await get_current_user(request)
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$addToSet": {"changelog_seen": changelog_id}}
    )
    return {"message": "ok"}


@admin_router.post("")
async def create_changelog(request: Request, admin: dict = Depends(require_admin)):
    """Create a new changelog entry (admin only)."""
    data = await request.json()
    doc = {
        "version": data.get("version", ""),
        "title": data.get("title", "What's New"),
        "subtitle": data.get("subtitle", ""),
        "sections": data.get("sections", []),
        "active": True,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.changelogs.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


@admin_router.delete("/{changelog_id}")
async def deactivate_changelog(changelog_id: str, admin: dict = Depends(require_admin)):
    """Deactivate a changelog (stops showing it to users)."""
    await db.changelogs.update_one(
        {"_id": ObjectId(changelog_id)},
        {"$set": {"active": False}}
    )
    return {"message": "Changelog deactivated"}
