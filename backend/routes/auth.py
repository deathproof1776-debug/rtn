"""
Authentication routes: register, login, logout, token refresh.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime, timezone, timedelta

from database import db, encrypt_data, decrypt_data
from auth import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    get_jwt_secret, JWT_ALGORITHM, get_current_user
)
from models import UserRegister, UserLogin
import jwt

router = APIRouter(prefix="/auth")


@router.post("/register")
async def register(user_data: UserRegister):
    # Validate invite token
    invite = await db.invites.find_one({"token": user_data.invite_token, "used": False})
    if not invite:
        raise HTTPException(status_code=403, detail="Invalid or expired invite link. You need a valid invitation from an existing member to join.")

    # Check if invite has expired (7 days)
    invite_created = datetime.fromisoformat(invite["created_at"])
    if datetime.now(timezone.utc) - invite_created > timedelta(days=7):
        raise HTTPException(status_code=403, detail="This invite link has expired. Please request a new one from a member.")

    email = user_data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed = hash_password(user_data.password)
    user_doc = {
        "email": email,
        "password_hash": hashed,
        "name": user_data.name,
        "location": encrypt_data(user_data.location) if user_data.location else "",
        "bio": "",
        "skills": [],
        "goods_offering": [],
        "goods_wanted": [],
        "services_offering": [],
        "services_wanted": [],
        "avatar": "",
        "role": "user",
        "is_verified": False,
        "invited_by": str(invite["created_by"]),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    # Mark invite as used
    await db.invites.update_one(
        {"_id": invite["_id"]},
        {"$set": {"used": True, "used_by": user_id, "used_at": datetime.now(timezone.utc).isoformat()}}
    )

    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)

    response = JSONResponse(content={
        "id": user_id,
        "email": email,
        "name": user_data.name,
        "message": "Registration successful"
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    return response


@router.post("/login")
async def login(user_data: UserLogin):
    email = user_data.email.lower()
    user = await db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user_data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)

    # Decrypt location for response
    location = ""
    if user.get("location"):
        try:
            location = decrypt_data(user["location"])
        except Exception:
            location = user.get("location", "")

    response = JSONResponse(content={
        "id": user_id,
        "email": email,
        "name": user.get("name", ""),
        "location": location,
        "avatar": user.get("avatar", ""),
        "is_verified": user.get("is_verified", False),
        "role": user.get("role", "user"),
        "message": "Login successful"
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=True, samesite="none", max_age=604800, path="/")
    return response


@router.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token", path="/", secure=True, samesite="none")
    response.delete_cookie(key="refresh_token", path="/", secure=True, samesite="none")
    return response


@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    # Decrypt encrypted fields
    if user.get("location"):
        try:
            user["location"] = decrypt_data(user["location"])
        except Exception:
            pass
    # Normalize _id to id for frontend consistency
    if "_id" in user:
        user["id"] = user.pop("_id")
    return user


@router.post("/refresh")
async def refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="No refresh token")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        access_token = create_access_token(str(user["_id"]), user["email"])
        response = JSONResponse(content={"message": "Token refreshed"})
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=True, samesite="none", max_age=3600, path="/")
        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
