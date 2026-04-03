"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    location: Optional[str] = ""
    invite_token: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class DetailedItem(BaseModel):
    """Item with optional description and quantity"""
    name: str
    description: Optional[str] = ""
    quantity: Optional[str] = ""


class UserProfile(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[Any]] = None
    goods_offering: Optional[List[Any]] = None
    goods_wanted: Optional[List[Any]] = None
    services_offering: Optional[List[Any]] = None
    services_wanted: Optional[List[Any]] = None
    avatar: Optional[str] = None


class CategorizedProfileUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    bio: Optional[str] = None
    skills: Optional[List[str]] = None
    goods_offering: Optional[List[str]] = None
    goods_wanted: Optional[List[str]] = None
    services_offering: Optional[List[str]] = None
    services_wanted: Optional[List[str]] = None
    avatar: Optional[str] = None
    custom_skills: Optional[List[str]] = None
    custom_goods_offering: Optional[List[str]] = None
    custom_goods_wanted: Optional[List[str]] = None
    custom_services_offering: Optional[List[str]] = None
    custom_services_wanted: Optional[List[str]] = None


class VerifyTraderRequest(BaseModel):
    user_id: str
    is_verified: bool


class BarterPost(BaseModel):
    title: str
    description: str
    category: str
    offering: List[Any]
    looking_for: List[Any]
    images: Optional[List[str]] = []


class MessageCreate(BaseModel):
    receiver_id: str
    content: str


class CommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None


class CommentReplyCreate(BaseModel):
    content: str
    parent_id: str


class PushSubscription(BaseModel):
    endpoint: str
    keys: Dict[str, str]


class InviteCreate(BaseModel):
    email: Optional[str] = None


class NetworkRequest(BaseModel):
    target_user_id: str


class NetworkRequestResponse(BaseModel):
    request_id: str
    accept: bool


class TradeOfferCreate(BaseModel):
    receiver_id: str
    offering: List[str]
    requesting: List[str]
    message: Optional[str] = ""
    post_id: Optional[str] = None


class TradeCounterOffer(BaseModel):
    offering: List[str]
    requesting: List[str]
    message: Optional[str] = ""


class TradeOfferRespond(BaseModel):
    action: str


class GalleryItemCreate(BaseModel):
    caption: Optional[str] = ""


class GalleryCommentCreate(BaseModel):
    content: str
    parent_id: Optional[str] = None


class UpdateUserRole(BaseModel):
    role: str


# Helper functions for item normalization
def normalize_items(items: List[Any]) -> List[Dict[str, str]]:
    """Convert mixed list of strings and dicts to consistent DetailedItem format"""
    if not items:
        return []
    result = []
    for item in items:
        if isinstance(item, str):
            result.append({"name": item, "description": "", "quantity": ""})
        elif isinstance(item, dict):
            result.append({
                "name": item.get("name", ""),
                "description": item.get("description", ""),
                "quantity": item.get("quantity", "")
            })
    return result


def get_item_names(items: List[Any]) -> List[str]:
    """Extract just the names from items for matching/search"""
    if not items:
        return []
    result = []
    for item in items:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            result.append(item.get("name", ""))
    return [n for n in result if n]
