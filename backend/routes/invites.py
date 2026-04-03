"""
Invite system routes: create and validate invite tokens.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import secrets

from database import db
from auth import get_current_user
from models import InviteCreate

router = APIRouter(prefix="/invites")


@router.post("/create")
async def create_invite(invite_data: InviteCreate, request: Request):
    """Generate a unique invite link. Only authenticated users can create invites."""
    user = await get_current_user(request)
    user_id = user["_id"]

    token = secrets.token_urlsafe(32)
    invite_doc = {
        "token": token,
        "created_by": user_id,
        "created_by_name": user.get("name", "Unknown"),
        "email": invite_data.email or None,
        "used": False,
        "used_by": None,
        "used_at": None,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.invites.insert_one(invite_doc)

    return {
        "token": token,
        "message": "Invite created successfully"
    }


@router.get("/validate/{token}")
async def validate_invite(token: str):
    """Public endpoint to check if an invite token is valid."""
    invite = await db.invites.find_one({"token": token, "used": False})
    if not invite:
        raise HTTPException(status_code=404, detail="Invalid or already used invite link")

    invite_created = datetime.fromisoformat(invite["created_at"])
    if datetime.now(timezone.utc) - invite_created > timedelta(days=7):
        raise HTTPException(status_code=410, detail="This invite link has expired")

    return {
        "valid": True,
        "invited_by": invite.get("created_by_name", "A network member")
    }


@router.get("/my-invites")
async def get_my_invites(request: Request):
    """Get all invites created by the current user."""
    user = await get_current_user(request)
    user_id = user["_id"]

    invites = await db.invites.find(
        {"created_by": user_id},
        {"_id": 0, "token": 1, "email": 1, "used": 1, "used_by": 1, "created_at": 1, "used_at": 1, "created_by_name": 1}
    ).sort("created_at", -1).to_list(50)

    for inv in invites:
        if inv.get("used_by"):
            used_user = await db.users.find_one({"_id": ObjectId(inv["used_by"])}, {"name": 1})
            inv["used_by_name"] = used_user["name"] if used_user else "Unknown"
        else:
            inv["used_by_name"] = None

    return invites
