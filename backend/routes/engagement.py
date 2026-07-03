"""
Engagement routes: one-time onboarding tour + achievement acknowledgement.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId

from database import db
from auth import get_current_user
from achievements import ACHIEVEMENTS

router = APIRouter()


@router.post("/onboarding/complete")
async def complete_onboarding(request: Request):
    """Mark the new-user onboarding tour as seen (shows only once)."""
    user = await get_current_user(request)
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"has_seen_onboarding": True}}
    )
    return {"message": "Onboarding completed"}


@router.post("/achievements/ack")
async def acknowledge_achievement(request: Request):
    """Dismiss a celebrated achievement so it won't show again."""
    user = await get_current_user(request)
    data = await request.json()
    key = (data.get("key") or "").strip()
    if key not in ACHIEVEMENTS:
        raise HTTPException(status_code=400, detail="Invalid achievement key")
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$pull": {"pending_achievements": key},
         "$addToSet": {"achievements_seen": key}}
    )
    return {"message": "Acknowledged"}
