"""
Profile routes: view and update user profiles.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId

from database import db, encrypt_data, safe_decrypt
from auth import get_current_user
from location import locations_match
from models import UserProfile, normalize_items

router = APIRouter()


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
    await get_current_user(request)
    user = await db.users.find_one({"_id": ObjectId(user_id)}, {"password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user["_id"] = str(user["_id"])
    user["location"] = safe_decrypt(user.get("location"))
    user["bio"] = safe_decrypt(user.get("bio"))
    return user


@router.get("/users/nearby")
async def get_nearby_users(request: Request):
    """Get users in the same location as the current user."""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    user_location = safe_decrypt(user_doc.get("location"))

    if not user_location:
        return {"nearby_users": [], "message": "Set your location to find nearby homesteaders"}

    all_users = await db.users.find(
        {"_id": {"$ne": ObjectId(user["_id"])}},
        {"password_hash": 0}
    ).limit(100).to_list(100)

    nearby_users = []
    for u in all_users:
        u_location = safe_decrypt(u.get("location"))
        if locations_match(user_location, u_location):
            nearby_users.append({
                "_id": str(u["_id"]),
                "name": u.get("name", "Unknown"),
                "avatar": u.get("avatar", ""),
                "location": u_location,
                "is_verified": u.get("is_verified", False)
            })

    return {"nearby_users": nearby_users}
