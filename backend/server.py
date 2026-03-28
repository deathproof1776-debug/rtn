from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import logging
import bcrypt
import jwt
import secrets
import json
import aiofiles
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
import base64
import hashlib
from pywebpush import webpush, WebPushException

ROOT_DIR = Path(__file__).parent

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# JWT Configuration
JWT_ALGORITHM = "HS256"

def get_jwt_secret() -> str:
    return os.environ["JWT_SECRET"]

# Encryption setup
def get_encryption_key():
    key = os.environ.get("ENCRYPTION_KEY", "default-encryption-key-32b!")
    key_bytes = hashlib.sha256(key.encode()).digest()
    return base64.urlsafe_b64encode(key_bytes)

fernet = Fernet(get_encryption_key())

def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return fernet.decrypt(encrypted_data.encode()).decode()

# VAPID Configuration for Push Notifications
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS_EMAIL = os.environ.get("VAPID_CLAIMS_EMAIL", "admin@homesteadhub.com")

# Push Notification Helper
async def send_push_notification(user_id: str, title: str, body: str, data: dict = None, icon: str = "/logo192.png"):
    """Send push notification to all subscribed devices of a user"""
    if not VAPID_PUBLIC_KEY or not VAPID_PRIVATE_KEY:
        logger.warning("VAPID keys not configured, skipping push notification")
        return
    
    subscriptions = await db.push_subscriptions.find({"user_id": user_id}).to_list(100)
    
    notification_payload = json.dumps({
        "title": title,
        "body": body,
        "icon": icon,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {
                        "p256dh": sub["keys"]["p256dh"],
                        "auth": sub["keys"]["auth"]
                    }
                },
                data=notification_payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{VAPID_CLAIMS_EMAIL}"}
            )
            logger.info(f"Push notification sent to user {user_id}")
        except WebPushException as e:
            logger.error(f"Push notification failed: {e}")
            # Remove invalid subscription (410 Gone or 404 Not Found)
            if e.response and e.response.status_code in [404, 410]:
                await db.push_subscriptions.delete_one({"_id": sub["_id"]})
                logger.info(f"Removed invalid subscription for user {user_id}")

# Password hashing
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

# JWT Token Management
def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id, 
        "email": email, 
        "exp": datetime.now(timezone.utc) + timedelta(minutes=60),
        "type": "access"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    payload = {
        "sub": user_id, 
        "exp": datetime.now(timezone.utc) + timedelta(days=7), 
        "type": "refresh"
    }
    return jwt.encode(payload, get_jwt_secret(), algorithm=JWT_ALGORITHM)

# Create app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        logger.info(f"User {user_id} connected via WebSocket")
    
    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            logger.info(f"User {user_id} disconnected")
    
    async def send_personal_message(self, message: dict, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json(message)

manager = ConnectionManager()

# Pydantic Models
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    location: Optional[str] = ""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    goods_offering: Optional[List[str]] = None
    goods_wanted: Optional[List[str]] = None
    services_offering: Optional[List[str]] = None
    services_wanted: Optional[List[str]] = None
    avatar: Optional[str] = None

class VerifyTraderRequest(BaseModel):
    user_id: str
    is_verified: bool

class BarterPost(BaseModel):
    title: str
    description: str
    category: str  # goods, services, skills
    offering: List[str]
    looking_for: List[str]
    images: Optional[List[str]] = []

class MessageCreate(BaseModel):
    receiver_id: str
    content: str

class CommentCreate(BaseModel):
    content: str

class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]  # Contains 'p256dh' and 'auth'

class NetworkRequest(BaseModel):
    target_user_id: str

class NetworkRequestResponse(BaseModel):
    request_id: str
    accept: bool

# Auth helper
async def get_current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=[JWT_ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user = await db.users.find_one({"_id": ObjectId(payload["sub"])})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        user["_id"] = str(user["_id"])
        user.pop("password_hash", None)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Auth routes
@api_router.post("/auth/register")
async def register(user_data: UserRegister):
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
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)
    
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id)
    
    response = JSONResponse(content={
        "id": user_id,
        "email": email,
        "name": user_data.name,
        "message": "Registration successful"
    })
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return response

@api_router.post("/auth/login")
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
    response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True, secure=False, samesite="lax", max_age=604800, path="/")
    return response

@api_router.post("/auth/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token", path="/")
    response.delete_cookie(key="refresh_token", path="/")
    return response

@api_router.get("/auth/me")
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

@api_router.post("/auth/refresh")
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
        response.set_cookie(key="access_token", value=access_token, httponly=True, secure=False, samesite="lax", max_age=3600, path="/")
        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

# Profile routes
@api_router.put("/profile")
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
        update_data["skills"] = profile.skills
    if profile.goods_offering is not None:
        update_data["goods_offering"] = profile.goods_offering
    if profile.goods_wanted is not None:
        update_data["goods_wanted"] = profile.goods_wanted
    if profile.services_offering is not None:
        update_data["services_offering"] = profile.services_offering
    if profile.services_wanted is not None:
        update_data["services_wanted"] = profile.services_wanted
    if profile.avatar is not None:
        update_data["avatar"] = profile.avatar
    
    await db.users.update_one({"_id": ObjectId(user["_id"])}, {"$set": update_data})
    return {"message": "Profile updated successfully"}

@api_router.get("/profile/{user_id}")
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

# Barter Posts routes
@api_router.post("/posts", status_code=201)
async def create_post(post: BarterPost, request: Request):
    user = await get_current_user(request)
    post_doc = {
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "title": post.title,
        "description": encrypt_data(post.description),
        "category": post.category,
        "offering": post.offering,
        "looking_for": post.looking_for,
        "images": post.images,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "likes": [],
        "comments": []
    }
    result = await db.posts.insert_one(post_doc)
    return {"id": str(result.inserted_id), "message": "Post created successfully"}

@api_router.get("/posts")
async def get_posts(request: Request, skip: int = 0, limit: int = 20, nearby_only: bool = False):
    user = await get_current_user(request)  # Verify auth
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    
    # Get user's trade network connections for priority
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
    
    # Decrypt user's location for nearby filtering
    user_location = ""
    if user_doc.get("location"):
        try:
            user_location = decrypt_data(user_doc["location"])
        except Exception:
            user_location = user_doc.get("location", "")
    
    posts = await db.posts.find({}, {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1, "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1, "likes": 1, "comments": 1}).sort("created_at", -1).skip(skip).limit(100 if nearby_only else limit * 3).to_list(100 if nearby_only else limit * 3)
    
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
        
        # Add location and verification info
        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False})
        poster_location = user_data["location"]
        post["user_location"] = poster_location
        post["is_nearby"] = locations_match(user_location, poster_location) if user_location else False
        post["is_verified"] = user_data["is_verified"]
        post["is_network"] = post["user_id"] in network_user_ids
        
        # Calculate feed priority score (network members get priority)
        feed_score = 0
        if post["is_network"]:
            feed_score += 200  # Network member priority
        if post.get("is_nearby"):
            feed_score += 100  # Location bonus
        post["feed_score"] = feed_score
        
        # Filter if nearby_only
        if nearby_only:
            if post["is_nearby"]:
                result_posts.append(post)
        else:
            result_posts.append(post)
    
    # Sort by feed_score (network + nearby first), then by date
    result_posts.sort(key=lambda x: (-x.get("feed_score", 0), x.get("created_at", "")), reverse=False)
    result_posts.sort(key=lambda x: -x.get("feed_score", 0))
    
    return result_posts[:limit]

def normalize_location(location: str) -> str:
    """Normalize location string for comparison (lowercase, strip whitespace)"""
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
    # Exact match
    if norm1 == norm2:
        return True
    # Check if one contains the other (e.g., "Austin" matches "Austin, TX")
    if norm1 in norm2 or norm2 in norm1:
        return True
    # Split by comma and check city/state parts
    parts1 = [p.strip() for p in norm1.split(',')]
    parts2 = [p.strip() for p in norm2.split(',')]
    # Check if any part matches
    for p1 in parts1:
        for p2 in parts2:
            if p1 and p2 and (p1 == p2 or p1 in p2 or p2 in p1):
                return True
    return False

@api_router.get("/posts/matches")
async def get_matched_posts(request: Request):
    """Get posts that match user's wants with others' offerings, prioritized by network + location"""
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
    
    user_wants = (user_doc.get("goods_wanted", []) + 
                  user_doc.get("services_wanted", []))
    user_offerings = (user_doc.get("goods_offering", []) + 
                      user_doc.get("services_offering", []))
    
    # Find posts where offering matches user's wants OR looking_for matches user's offerings
    query = {"user_id": {"$ne": user["_id"]}}
    if user_wants or user_offerings:
        or_conditions = []
        if user_wants:
            or_conditions.append({"offering": {"$in": user_wants}})
        if user_offerings:
            or_conditions.append({"looking_for": {"$in": user_offerings}})
        if or_conditions:
            query["$or"] = or_conditions
    
    posts = await db.posts.find(query, {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1, "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1}).sort("created_at", -1).limit(50).to_list(50)
    
    # Get user locations and verification status for sorting and add location info
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
    
    # Add location and match score to posts
    for post in posts:
        post["_id"] = str(post["_id"])
        if post.get("description"):
            try:
                post["description"] = decrypt_data(post["description"])
            except Exception:
                pass
        
        # Add location and verification info
        user_data = users_map.get(post["user_id"], {"location": "", "is_verified": False})
        poster_location = user_data["location"]
        post["user_location"] = poster_location
        post["is_nearby"] = locations_match(user_location, poster_location) if user_location else False
        post["is_verified"] = user_data["is_verified"]
        post["is_network"] = post["user_id"] in network_user_ids
        
        # Calculate match score (higher = better) - Network members get top priority
        score = 0
        if post["is_network"]:
            score += 200  # Network member priority (highest)
        if post.get("is_nearby"):
            score += 100  # Location match bonus
        # Check goods/services match
        post_offerings = post.get("offering", [])
        post_looking = post.get("looking_for", [])
        for item in post_offerings:
            if item in user_wants:
                score += 10
        for item in post_looking:
            if item in user_offerings:
                score += 10
        post["match_score"] = score
    
    # Sort by match_score (network + nearby + relevant first), then by date
    posts.sort(key=lambda x: (-x.get("match_score", 0), x.get("created_at", "")), reverse=False)
    posts.sort(key=lambda x: -x.get("match_score", 0))
    
    return posts[:20]

@api_router.post("/posts/{post_id}/like")
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
        
        # Send push notification to post owner (if not self-like)
        if post["user_id"] != user["_id"]:
            background_tasks.add_task(
                send_push_notification,
                user_id=post["user_id"],
                title=f"{user.get('name', 'Someone')} liked your post",
                body=post.get("title", "Your barter post")[:50],
                data={"type": "like", "post_id": post_id, "url": "/"}
            )
        
        return {"message": "Post liked"}

# Comments routes
@api_router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: str, comment: CommentCreate, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)
    
    # Validate comment content
    if not comment.content or not comment.content.strip():
        raise HTTPException(status_code=400, detail="Comment content cannot be empty")
    
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comment_doc = {
        "id": str(ObjectId()),
        "user_id": user["_id"],
        "user_name": user.get("name", "Anonymous"),
        "user_avatar": user.get("avatar", ""),
        "content": encrypt_data(comment.content),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$push": {"comments": comment_doc}}
    )
    
    # Send push notification to post owner (if not self-comment)
    if post["user_id"] != user["_id"]:
        background_tasks.add_task(
            send_push_notification,
            user_id=post["user_id"],
            title=f"{user.get('name', 'Someone')} commented on your post",
            body=comment.content[:100] + ("..." if len(comment.content) > 100 else ""),
            data={"type": "comment", "post_id": post_id, "url": "/"}
        )
    
    # Return decrypted content for frontend
    return {
        "id": comment_doc["id"],
        "user_id": comment_doc["user_id"],
        "user_name": comment_doc["user_name"],
        "user_avatar": comment_doc["user_avatar"],
        "content": comment.content,
        "created_at": comment_doc["created_at"]
    }

@api_router.get("/posts/{post_id}/comments")
async def get_comments(post_id: str, request: Request):
    await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)}, {"comments": 1})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = post.get("comments", [])
    # Decrypt comment content
    for comment in comments:
        if comment.get("content"):
            try:
                comment["content"] = decrypt_data(comment["content"])
            except Exception:
                pass
    
    return comments

@api_router.delete("/posts/{post_id}/comments/{comment_id}")
async def delete_comment(post_id: str, comment_id: str, request: Request):
    user = await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Find the comment and verify ownership
    comment_to_delete = None
    for comment in post.get("comments", []):
        if comment.get("id") == comment_id:
            comment_to_delete = comment
            break
    
    if not comment_to_delete:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    # Allow deletion if user owns the comment or the post
    if comment_to_delete["user_id"] != user["_id"] and post["user_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    
    await db.posts.update_one(
        {"_id": ObjectId(post_id)},
        {"$pull": {"comments": {"id": comment_id}}}
    )
    
    return {"message": "Comment deleted"}

# Messaging routes
@api_router.get("/conversations")
async def get_conversations(request: Request):
    user = await get_current_user(request)
    user_id = user["_id"]
    
    # Get unique conversations
    pipeline = [
        {"$match": {"$or": [{"sender_id": user_id}, {"receiver_id": user_id}]}},
        {"$sort": {"created_at": -1}},
        {"$group": {
            "_id": {"$cond": [{"$eq": ["$sender_id", user_id]}, "$receiver_id", "$sender_id"]},
            "last_message": {"$first": "$content"},
            "last_message_at": {"$first": "$created_at"},
            "unread_count": {"$sum": {"$cond": [{"$and": [{"$eq": ["$receiver_id", user_id]}, {"$eq": ["$read", False]}]}, 1, 0]}}
        }}
    ]
    
    conversations = await db.messages.aggregate(pipeline).to_list(50)
    
    # Get user details for each conversation
    result = []
    for conv in conversations:
        other_user = await db.users.find_one({"_id": ObjectId(conv["_id"])}, {"password_hash": 0})
        if other_user:
            # Decrypt last message
            last_msg = conv.get("last_message", "")
            try:
                last_msg = decrypt_data(last_msg)
            except Exception:
                pass
            
            result.append({
                "user_id": str(other_user["_id"]),
                "user_name": other_user.get("name", "Unknown"),
                "user_avatar": other_user.get("avatar", ""),
                "last_message": last_msg[:50] + "..." if len(last_msg) > 50 else last_msg,
                "last_message_at": conv.get("last_message_at"),
                "unread_count": conv.get("unread_count", 0)
            })
    
    return result

@api_router.get("/messages/{other_user_id}")
async def get_messages(other_user_id: str, request: Request, skip: int = 0, limit: int = 50):
    user = await get_current_user(request)
    user_id = user["_id"]
    
    messages = await db.messages.find({
        "$or": [
            {"sender_id": user_id, "receiver_id": other_user_id},
            {"sender_id": other_user_id, "receiver_id": user_id}
        ]
    }).sort("created_at", 1).skip(skip).limit(limit).to_list(limit)
    
    # Mark messages as read
    await db.messages.update_many(
        {"sender_id": other_user_id, "receiver_id": user_id, "read": False},
        {"$set": {"read": True}}
    )
    
    result = []
    for msg in messages:
        content = msg.get("content", "")
        try:
            content = decrypt_data(content)
        except Exception:
            pass
        result.append({
            "id": str(msg["_id"]),
            "sender_id": msg["sender_id"],
            "receiver_id": msg["receiver_id"],
            "content": content,
            "created_at": msg["created_at"],
            "read": msg.get("read", False)
        })
    
    return result

@api_router.post("/messages")
async def send_message(message: MessageCreate, request: Request, background_tasks: BackgroundTasks):
    user = await get_current_user(request)
    
    msg_doc = {
        "sender_id": user["_id"],
        "receiver_id": message.receiver_id,
        "content": encrypt_data(message.content),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "read": False
    }
    result = await db.messages.insert_one(msg_doc)
    
    # Send via WebSocket if receiver is connected
    await manager.send_personal_message({
        "type": "new_message",
        "id": str(result.inserted_id),
        "sender_id": user["_id"],
        "sender_name": user.get("name", "Unknown"),
        "content": message.content,
        "created_at": msg_doc["created_at"]
    }, message.receiver_id)
    
    # Send push notification to receiver
    background_tasks.add_task(
        send_push_notification,
        user_id=message.receiver_id,
        title=f"New message from {user.get('name', 'Someone')}",
        body=message.content[:100] + ("..." if len(message.content) > 100 else ""),
        data={"type": "message", "sender_id": user["_id"], "url": "/messages"}
    )
    
    return {"id": str(result.inserted_id), "message": "Message sent"}

# File upload
@api_router.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    await get_current_user(request)  # Verify auth
    
    # Create uploads directory if not exists
    upload_dir = ROOT_DIR / "uploads"
    upload_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    ext = Path(file.filename).suffix
    filename = f"{secrets.token_hex(16)}{ext}"
    filepath = upload_dir / filename
    
    async with aiofiles.open(filepath, 'wb') as f:
        content = await file.read()
        await f.write(content)
    
    return {"url": f"/api/uploads/{filename}", "filename": filename}

@api_router.get("/uploads/{filename}")
async def get_upload(filename: str):
    filepath = ROOT_DIR / "uploads" / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)

# Get nearby users (location-based user matching)
@api_router.get("/users/nearby")
async def get_nearby_users(request: Request, limit: int = 20):
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
        u["_id"] = str(u["_id"])
        u_location = ""
        if u.get("location"):
            try:
                u_location = decrypt_data(u["location"])
            except Exception:
                u_location = u.get("location", "")
        
        if locations_match(user_location, u_location):
            u["location"] = u_location
            # Decrypt bio if present
            if u.get("bio"):
                try:
                    u["bio"] = decrypt_data(u["bio"])
                except Exception:
                    pass
            nearby_users.append(u)
    
    return {"nearby_users": nearby_users[:limit], "user_location": user_location, "count": len(nearby_users)}

# Search users
@api_router.get("/users/search")
async def search_users(request: Request, q: str = "", skill: str = "", good: str = "", service: str = ""):
    await get_current_user(request)
    
    query = {}
    conditions = []
    
    if q:
        conditions.append({"name": {"$regex": q, "$options": "i"}})
    if skill:
        conditions.append({"skills": {"$in": [skill]}})
    if good:
        conditions.append({"$or": [{"goods_offering": {"$in": [good]}}, {"goods_wanted": {"$in": [good]}}]})
    if service:
        conditions.append({"$or": [{"services_offering": {"$in": [service]}}, {"services_wanted": {"$in": [service]}}]})
    
    if conditions:
        query = {"$and": conditions} if len(conditions) > 1 else conditions[0]
    
    users = await db.users.find(query, {"password_hash": 0}).limit(50).to_list(50)
    
    for user in users:
        user["_id"] = str(user["_id"])
        if user.get("location"):
            try:
                user["location"] = decrypt_data(user["location"])
            except Exception:
                pass
    
    return users

# Admin: Verify/Unverify Trader
@api_router.post("/admin/verify-trader")
async def verify_trader(data: VerifyTraderRequest, request: Request):
    """Admin endpoint to verify/unverify a trader"""
    admin_user = await get_current_user(request)
    
    # Check if current user is admin
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Find user to verify
    target_user = await db.users.find_one({"_id": ObjectId(data.user_id)})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update verification status
    await db.users.update_one(
        {"_id": ObjectId(data.user_id)},
        {"$set": {"is_verified": data.is_verified, "verified_at": datetime.now(timezone.utc).isoformat() if data.is_verified else None}}
    )
    
    return {
        "message": f"Trader {'verified' if data.is_verified else 'unverified'} successfully",
        "user_id": data.user_id,
        "is_verified": data.is_verified
    }

# Admin: Get all users for admin panel
@api_router.get("/admin/users")
async def get_all_users(request: Request, skip: int = 0, limit: int = 50):
    """Admin endpoint to get all users"""
    admin_user = await get_current_user(request)
    
    if admin_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    users = await db.users.find({}, {"password_hash": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
    for user in users:
        user["_id"] = str(user["_id"])
        if user.get("location"):
            try:
                user["location"] = decrypt_data(user["location"])
            except Exception:
                pass
    
    total = await db.users.count_documents({})
    return {"users": users, "total": total}

# Push Notification endpoints
@api_router.get("/notifications/vapid-public-key")
async def get_vapid_public_key():
    """Get VAPID public key for frontend push subscription"""
    return {"publicKey": VAPID_PUBLIC_KEY}

@api_router.post("/notifications/subscribe")
async def subscribe_push(subscription: PushSubscription, request: Request):
    """Subscribe to push notifications"""
    user = await get_current_user(request)
    
    # Check if subscription already exists
    existing = await db.push_subscriptions.find_one({
        "user_id": user["_id"],
        "endpoint": subscription.endpoint
    })
    
    if existing:
        return {"message": "Already subscribed", "subscribed": True}
    
    # Save subscription
    sub_doc = {
        "user_id": user["_id"],
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.push_subscriptions.insert_one(sub_doc)
    
    return {"message": "Subscribed to push notifications", "subscribed": True}

@api_router.post("/notifications/unsubscribe")
async def unsubscribe_push(subscription: PushSubscription, request: Request):
    """Unsubscribe from push notifications"""
    user = await get_current_user(request)
    
    result = await db.push_subscriptions.delete_one({
        "user_id": user["_id"],
        "endpoint": subscription.endpoint
    })
    
    if result.deleted_count > 0:
        return {"message": "Unsubscribed from push notifications", "subscribed": False}
    return {"message": "Subscription not found", "subscribed": False}

@api_router.get("/notifications/status")
async def get_notification_status(request: Request):
    """Get user's push notification subscription status"""
    user = await get_current_user(request)
    
    count = await db.push_subscriptions.count_documents({"user_id": user["_id"]})
    return {"subscribed": count > 0, "subscription_count": count}

@api_router.post("/notifications/test")
async def test_push_notification(request: Request):
    """Send a test push notification to the current user"""
    user = await get_current_user(request)
    
    await send_push_notification(
        user_id=user["_id"],
        title="Rebel Trade Network Test",
        body="Push notifications are working! You'll receive alerts for messages, comments, and matches.",
        data={"type": "test", "url": "/"}
    )
    
    return {"message": "Test notification sent"}

# ========================
# Trade Network Endpoints
# ========================

@api_router.post("/network/request")
async def send_network_request(data: NetworkRequest, request: Request, background_tasks: BackgroundTasks):
    """Send a trade network request to another user"""
    user = await get_current_user(request)
    target_user_id = data.target_user_id
    
    # Can't send request to self
    if target_user_id == user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot send network request to yourself")
    
    # Check if target user exists
    target_user = await db.users.find_one({"_id": ObjectId(target_user_id)})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already connected
    existing_connection = await db.network_connections.find_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": target_user_id},
            {"user_id": target_user_id, "connected_user_id": user["_id"]}
        ]
    })
    if existing_connection:
        raise HTTPException(status_code=400, detail="Already in trade network")
    
    # Check if request already exists (either direction)
    existing_request = await db.network_requests.find_one({
        "$or": [
            {"from_user_id": user["_id"], "to_user_id": target_user_id, "status": "pending"},
            {"from_user_id": target_user_id, "to_user_id": user["_id"], "status": "pending"}
        ]
    })
    if existing_request:
        raise HTTPException(status_code=400, detail="Network request already pending")
    
    # Create request
    request_doc = {
        "from_user_id": user["_id"],
        "from_user_name": user.get("name", "Unknown"),
        "from_user_avatar": user.get("avatar", ""),
        "to_user_id": target_user_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.network_requests.insert_one(request_doc)
    
    # Send push notification to target user
    background_tasks.add_task(
        send_push_notification,
        user_id=target_user_id,
        title="New Trade Network Request",
        body=f"{user.get('name', 'Someone')} wants to join your trade network",
        data={"type": "network_request", "from_user_id": user["_id"], "url": "/network"}
    )
    
    return {"id": str(result.inserted_id), "message": "Network request sent"}

@api_router.post("/network/respond")
async def respond_to_network_request(data: NetworkRequestResponse, request: Request, background_tasks: BackgroundTasks):
    """Accept or decline a network request"""
    user = await get_current_user(request)
    request_id = data.request_id
    
    # Find the request
    network_request = await db.network_requests.find_one({
        "_id": ObjectId(request_id),
        "to_user_id": user["_id"],
        "status": "pending"
    })
    
    if not network_request:
        raise HTTPException(status_code=404, detail="Network request not found")
    
    from_user_id = network_request["from_user_id"]
    
    if data.accept:
        # Create bidirectional connection
        connection_doc = {
            "user_id": user["_id"],
            "connected_user_id": from_user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.network_connections.insert_one(connection_doc)
        
        # Update request status
        await db.network_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "accepted", "responded_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Send push notification to requester
        background_tasks.add_task(
            send_push_notification,
            user_id=from_user_id,
            title="Network Request Accepted",
            body=f"{user.get('name', 'Someone')} accepted your trade network request",
            data={"type": "network_accepted", "user_id": user["_id"], "url": "/network"}
        )
        
        return {"message": "Network request accepted", "connected": True}
    else:
        # Decline request
        await db.network_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "declined", "responded_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"message": "Network request declined", "connected": False}

@api_router.get("/network/requests/pending")
async def get_pending_requests(request: Request):
    """Get pending network requests for current user"""
    user = await get_current_user(request)
    
    # Incoming requests
    incoming = await db.network_requests.find({
        "to_user_id": user["_id"],
        "status": "pending"
    }).sort("created_at", -1).to_list(50)
    
    # Outgoing requests
    outgoing = await db.network_requests.find({
        "from_user_id": user["_id"],
        "status": "pending"
    }).sort("created_at", -1).to_list(50)
    
    # Format responses
    incoming_formatted = []
    for req in incoming:
        from_user = await db.users.find_one({"_id": ObjectId(req["from_user_id"])}, {"password_hash": 0})
        if from_user:
            incoming_formatted.append({
                "id": str(req["_id"]),
                "from_user_id": req["from_user_id"],
                "from_user_name": from_user.get("name", "Unknown"),
                "from_user_avatar": from_user.get("avatar", ""),
                "is_verified": from_user.get("is_verified", False),
                "created_at": req["created_at"]
            })
    
    outgoing_formatted = []
    for req in outgoing:
        to_user = await db.users.find_one({"_id": ObjectId(req["to_user_id"])}, {"password_hash": 0})
        if to_user:
            outgoing_formatted.append({
                "id": str(req["_id"]),
                "to_user_id": req["to_user_id"],
                "to_user_name": to_user.get("name", "Unknown"),
                "to_user_avatar": to_user.get("avatar", ""),
                "is_verified": to_user.get("is_verified", False),
                "created_at": req["created_at"]
            })
    
    return {
        "incoming": incoming_formatted,
        "outgoing": outgoing_formatted,
        "incoming_count": len(incoming_formatted)
    }

@api_router.get("/network/connections")
async def get_network_connections(request: Request):
    """Get all users in the current user's trade network"""
    user = await get_current_user(request)
    
    # Find all connections (bidirectional lookup)
    connections = await db.network_connections.find({
        "$or": [
            {"user_id": user["_id"]},
            {"connected_user_id": user["_id"]}
        ]
    }).to_list(500)
    
    # Get unique connected user IDs
    connected_user_ids = set()
    for conn in connections:
        if conn["user_id"] == user["_id"]:
            connected_user_ids.add(conn["connected_user_id"])
        else:
            connected_user_ids.add(conn["user_id"])
    
    # Fetch user details
    network_users = []
    for uid in connected_user_ids:
        u = await db.users.find_one({"_id": ObjectId(uid)}, {"password_hash": 0})
        if u:
            u["_id"] = str(u["_id"])
            # Decrypt location
            if u.get("location"):
                try:
                    u["location"] = decrypt_data(u["location"])
                except Exception:
                    pass
            network_users.append({
                "id": u["_id"],
                "name": u.get("name", "Unknown"),
                "avatar": u.get("avatar", ""),
                "location": u.get("location", ""),
                "skills": u.get("skills", []),
                "goods_offering": u.get("goods_offering", []),
                "services_offering": u.get("services_offering", []),
                "is_verified": u.get("is_verified", False)
            })
    
    return {"connections": network_users, "count": len(network_users)}

@api_router.delete("/network/connections/{user_id}")
async def remove_from_network(user_id: str, request: Request):
    """Remove a user from your trade network"""
    user = await get_current_user(request)
    
    # Delete connection (either direction)
    result = await db.network_connections.delete_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": user_id},
            {"user_id": user_id, "connected_user_id": user["_id"]}
        ]
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    return {"message": "Removed from trade network"}

@api_router.get("/network/status/{user_id}")
async def get_network_status(user_id: str, request: Request):
    """Check network status with another user"""
    user = await get_current_user(request)
    
    # Check if connected
    connection = await db.network_connections.find_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": user_id},
            {"user_id": user_id, "connected_user_id": user["_id"]}
        ]
    })
    
    if connection:
        return {"status": "connected", "can_request": False}
    
    # Check for pending request
    pending = await db.network_requests.find_one({
        "$or": [
            {"from_user_id": user["_id"], "to_user_id": user_id, "status": "pending"},
            {"from_user_id": user_id, "to_user_id": user["_id"], "status": "pending"}
        ]
    })
    
    if pending:
        if pending["from_user_id"] == user["_id"]:
            return {"status": "pending_sent", "can_request": False, "request_id": str(pending["_id"])}
        else:
            return {"status": "pending_received", "can_request": False, "request_id": str(pending["_id"])}
    
    return {"status": "none", "can_request": True}

@api_router.post("/network/cancel/{request_id}")
async def cancel_network_request(request_id: str, request: Request):
    """Cancel a pending network request that you sent"""
    user = await get_current_user(request)
    
    result = await db.network_requests.delete_one({
        "_id": ObjectId(request_id),
        "from_user_id": user["_id"],
        "status": "pending"
    })
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Request not found or already processed")
    
    return {"message": "Network request cancelled"}

# WebSocket endpoint
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    # Verify token from query params
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return
    
    # Verify user exists and token matches user_id (simplified MVP auth)
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user or token != user_id:
        await websocket.close(code=4001)
        return
    
    await manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            if message_data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message_data.get("type") == "message":
                # Handle incoming message
                receiver_id = message_data.get("receiver_id")
                content = message_data.get("content")
                
                if receiver_id and content:
                    msg_doc = {
                        "sender_id": user_id,
                        "receiver_id": receiver_id,
                        "content": encrypt_data(content),
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "read": False
                    }
                    result = await db.messages.insert_one(msg_doc)
                    
                    # Get sender info
                    sender = await db.users.find_one({"_id": ObjectId(user_id)})
                    sender_name = sender.get("name", "Unknown") if sender else "Unknown"
                    
                    # Send to receiver if online
                    await manager.send_personal_message({
                        "type": "new_message",
                        "id": str(result.inserted_id),
                        "sender_id": user_id,
                        "sender_name": sender_name,
                        "content": content,
                        "created_at": msg_doc["created_at"]
                    }, receiver_id)
                    
                    # Confirm to sender
                    await websocket.send_json({
                        "type": "message_sent",
                        "id": str(result.inserted_id),
                        "receiver_id": receiver_id,
                        "content": content,
                        "created_at": msg_doc["created_at"]
                    })
    except WebSocketDisconnect:
        manager.disconnect(user_id)

# Health check
@api_router.get("/")
async def root():
    return {"message": "Rebel Trade Network API", "status": "running"}

# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[os.environ.get("FRONTEND_URL", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Admin seeding
@app.on_event("startup")
async def startup():
    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.messages.create_index([("sender_id", 1), ("receiver_id", 1)])
    await db.posts.create_index("created_at")
    await db.push_subscriptions.create_index([("user_id", 1), ("endpoint", 1)], unique=True)
    # Trade Network indexes
    await db.network_connections.create_index([("user_id", 1), ("connected_user_id", 1)], unique=True)
    await db.network_requests.create_index([("from_user_id", 1), ("to_user_id", 1)])
    await db.network_requests.create_index("status")
    
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@rebeltrade.network")
    admin_password = os.environ.get("ADMIN_PASSWORD", "admin123")
    existing = await db.users.find_one({"email": admin_email})
    
    if existing is None:
        hashed = hash_password(admin_password)
        await db.users.insert_one({
            "email": admin_email,
            "password_hash": hashed,
            "name": "Admin",
            "location": "",
            "bio": "",
            "skills": ["Community Management", "Trading"],
            "goods_offering": [],
            "goods_wanted": [],
            "services_offering": [],
            "services_wanted": [],
            "avatar": "",
            "role": "admin",
            "is_verified": True,
            "created_at": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"Admin user created: {admin_email}")
    elif not verify_password(admin_password, existing["password_hash"]):
        await db.users.update_one({"email": admin_email}, {"$set": {"password_hash": hash_password(admin_password)}})
        logger.info("Admin password updated")
    
    # Write test credentials
    Path("/app/memory").mkdir(exist_ok=True)
    with open("/app/memory/test_credentials.md", "w") as f:
        f.write("# Test Credentials\n\n")
        f.write("## Admin Account\n")
        f.write(f"- Email: {admin_email}\n")
        f.write(f"- Password: {admin_password}\n")
        f.write("- Role: admin\n\n")
        f.write("## Auth Endpoints\n")
        f.write("- POST /api/auth/register\n")
        f.write("- POST /api/auth/login\n")
        f.write("- POST /api/auth/logout\n")
        f.write("- GET /api/auth/me\n")
        f.write("- POST /api/auth/refresh\n")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
