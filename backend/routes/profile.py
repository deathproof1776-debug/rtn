"""
Profile routes: view and update user profiles.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from models import UserProfile, normalize_items

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


@router.put("/profile")
async def update_profile(profile: UserProfile, request: Request):
    user = await get_current_user(request)
    update_data = {}

    if profile.name is not None:
        update_data["name"] = profile.name
    if profile.location is not None:
        update_data["location"] = encrypt_data(profile.location)
    if profile.bio is not None:
        update_data["bio"] = encrypt_data(profile.bio)
    if profile.skills is not None:
        update_data["skills"] = normalize_items(profile.skills)
    if profile.goods_offering is not None:
        update_data["goods_offering"] = normalize_items(profile.goods_offering)
    if profile.goods_wanted is not None:
        update_data["goods_wanted"] = normalize_items(profile.goods_wanted)
    if profile.services_offering is not None:
        update_data["services_offering"] = normalize_items(profile.services_offering)
    if profile.services_wanted is not None:
        update_data["services_wanted"] = normalize_items(profile.services_wanted)
    if profile.avatar is not None:
        update_data["avatar"] = profile.avatar

    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    return {"message": "Profile updated successfully"}


@router.get("/profile/{user_id}")
async def get_profile(user_id: str, request: Request):
    await get_current_user(request)  # Ensure authenticated
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    # Decrypt fields
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
    return user


@router.get("/users/nearby")
async def get_nearby_users(request: Request):
    """Get users in the same location as the current user"""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    
    # Decrypt user's location
    user_location = ""
    if user_doc.get("location"):
        try:
            user_location = decrypt_data(user_doc["location"])
        except Exception:
            user_location = user_doc.get("location", "")
    
    if not user_location:
        return {"nearby_users": [], "message": "Set your location to find nearby homesteaders"}
    
    # Get all users except current user
    all_users = await db.users.find(
        {"_id": {"$ne": ObjectId(user["_id"])}},
        {"password_hash": 0}
    ).limit(100).to_list(100)
    
    nearby_users = []
    for u in all_users:
        u_location = ""
        if u.get("location"):
            try:
                u_location = decrypt_data(u["location"])
            except Exception:
                u_location = u.get("location", "")
        
        if locations_match(user_location, u_location):
            nearby_users.append({
                "_id": str(u["_id"]),
                "name": u.get("name", "Unknown"),
                "avatar": u.get("avatar", ""),
                "location": u_location,
                "is_verified": u.get("is_verified", False)
            })
    
    return {"nearby_users": nearby_users}
