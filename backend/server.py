from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, APIRouter, HTTPException, Request, Depends, WebSocket, WebSocketDisconnect, UploadFile, File, Form
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
async def get_posts(request: Request, skip: int = 0, limit: int = 20):
    await get_current_user(request)  # Verify auth
    posts = await db.posts.find({}, {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1, "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1, "likes": 1, "comments": 1}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
    
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
    return posts

@api_router.get("/posts/matches")
async def get_matched_posts(request: Request):
    """Get posts that match user's wants with others' offerings"""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})
    
    user_wants = (user_doc.get("goods_wanted", []) + 
                  user_doc.get("services_wanted", []))
    
    if not user_wants:
        return []
    
    # Find posts where offering matches user's wants
    query = {
        "user_id": {"$ne": user["_id"]},
        "$or": [
            {"offering": {"$in": user_wants}},
            {"looking_for": {"$in": user_doc.get("goods_offering", []) + user_doc.get("services_offering", [])}}
        ]
    }
    
    posts = await db.posts.find(query, {"_id": 1, "user_id": 1, "user_name": 1, "user_avatar": 1, "title": 1, "description": 1, "category": 1, "offering": 1, "looking_for": 1, "images": 1, "created_at": 1}).sort("created_at", -1).limit(20).to_list(20)
    
    for post in posts:
        post["_id"] = str(post["_id"])
        if post.get("description"):
            try:
                post["description"] = decrypt_data(post["description"])
            except Exception:
                pass
    return posts

@api_router.post("/posts/{post_id}/like")
async def like_post(post_id: str, request: Request):
    user = await get_current_user(request)
    post = await db.posts.find_one({"_id": ObjectId(post_id)})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if user["_id"] in post.get("likes", []):
        await db.posts.update_one({"_id": ObjectId(post_id)}, {"$pull": {"likes": user["_id"]}})
        return {"message": "Post unliked"}
    else:
        await db.posts.update_one({"_id": ObjectId(post_id)}, {"$addToSet": {"likes": user["_id"]}})
        return {"message": "Post liked"}

# Comments routes
@api_router.post("/posts/{post_id}/comments", status_code=201)
async def create_comment(post_id: str, comment: CommentCreate, request: Request):
    user = await get_current_user(request)
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
async def send_message(message: MessageCreate, request: Request):
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
    return {"message": "HomesteadHub API", "status": "running"}

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
    
    # Seed admin
    admin_email = os.environ.get("ADMIN_EMAIL", "admin@homesteadhub.com")
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
            "skills": ["Community Management", "Homesteading"],
            "goods_offering": [],
            "goods_wanted": [],
            "services_offering": [],
            "services_wanted": [],
            "avatar": "",
            "role": "admin",
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
