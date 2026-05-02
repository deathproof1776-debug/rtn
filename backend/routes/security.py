"""
Account security routes: 2FA enrollment, session management,
"log out everywhere", and password change.
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from bson import ObjectId
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional

from database import db
from auth import get_current_user, hash_password, verify_password
from security import (
    generate_totp_secret, totp_provisioning_uri, totp_qr_data_url,
    verify_totp, generate_recovery_codes, store_recovery_codes,
    validate_password_strength, revoke_all_user_sessions,
    revoke_session_by_id,
)


router = APIRouter(prefix="/security")


# ============================================================
# 2FA: enroll, confirm, disable
# ============================================================
@router.post("/2fa/setup")
async def setup_2fa(request: Request):
    user = await get_current_user(request)
    if user.get("two_factor_enabled"):
        raise HTTPException(status_code=400, detail="2FA is already enabled.")

    secret = generate_totp_secret()
    uri = totp_provisioning_uri(secret, user.get("email", "user"))
    qr = totp_qr_data_url(uri)

    # Store as pending until user confirms
    await db.users.update_one(
        {"_id": ObjectId(user["_id"])},
        {"$set": {"totp_pending_secret": secret}}
    )
    return {
        "secret": secret,
        "otpauth_uri": uri,
        "qr_code": qr,
        "issuer": "Rebel Trade Network",
    }


class Confirm2FABody(BaseModel):
    code: str


@router.post("/2fa/confirm")
async def confirm_2fa(body: Confirm2FABody, request: Request):
    user = await get_current_user(request)
    fresh = await db.users.find_one({"_id": ObjectId(user["_id"])})
    secret = fresh.get("totp_pending_secret")
    if not secret:
        raise HTTPException(status_code=400, detail="No pending 2FA enrollment. Start setup first.")

    if not verify_totp(secret, body.code):
        raise HTTPException(status_code=400, detail="Invalid authenticator code.")

    codes = generate_recovery_codes()
    await store_recovery_codes(str(fresh["_id"]), codes)

    await db.users.update_one(
        {"_id": fresh["_id"]},
        {"$set": {
            "totp_secret": secret,
            "two_factor_enabled": True,
            "two_factor_enabled_at": datetime.now(timezone.utc).isoformat(),
        }, "$unset": {"totp_pending_secret": ""}}
    )
    return {"message": "Two-factor authentication enabled.", "recovery_codes": codes}


class Disable2FABody(BaseModel):
    password: str
    code: Optional[str] = None


@router.post("/2fa/disable")
async def disable_2fa(body: Disable2FABody, request: Request):
    user = await get_current_user(request)
    fresh = await db.users.find_one({"_id": ObjectId(user["_id"])})
    if not fresh:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(body.password, fresh["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect password.")
    if fresh.get("two_factor_enabled"):
        # Require fresh TOTP code to disable
        if not body.code or not verify_totp(fresh.get("totp_secret", ""), body.code):
            raise HTTPException(status_code=401, detail="Invalid authenticator code.")
    await db.users.update_one(
        {"_id": fresh["_id"]},
        {"$set": {"two_factor_enabled": False},
         "$unset": {"totp_secret": "", "totp_pending_secret": ""}}
    )
    await db.recovery_codes.delete_many({"user_id": str(fresh["_id"])})
    return {"message": "Two-factor authentication disabled."}


@router.post("/2fa/recovery-codes/regenerate")
async def regenerate_recovery_codes(request: Request):
    user = await get_current_user(request)
    fresh = await db.users.find_one({"_id": ObjectId(user["_id"])})
    if not fresh.get("two_factor_enabled"):
        raise HTTPException(status_code=400, detail="2FA is not enabled.")
    codes = generate_recovery_codes()
    await store_recovery_codes(str(fresh["_id"]), codes)
    return {"recovery_codes": codes}


# ============================================================
# Sessions: list / revoke / log out everywhere
# ============================================================
@router.get("/sessions")
async def list_sessions(request: Request):
    user = await get_current_user(request)
    current_refresh = request.cookies.get("refresh_token")
    current_sid = None
    if current_refresh:
        from security import _hash_token
        rec = await db.refresh_tokens.find_one({"token_hash": _hash_token(current_refresh)})
        if rec:
            current_sid = rec.get("session_id")
    sessions = await db.refresh_tokens.find(
        {"user_id": user["_id"], "revoked": False}
    ).sort("last_used_at", -1).to_list(50)
    out = []
    for s in sessions:
        out.append({
            "session_id": s.get("session_id"),
            "user_agent": s.get("user_agent", ""),
            "ip": s.get("ip", ""),
            "created_at": s.get("created_at"),
            "last_used_at": s.get("last_used_at"),
            "expires_at": s.get("expires_at"),
            "current": s.get("session_id") == current_sid,
        })
    return {"sessions": out}


class RevokeSessionBody(BaseModel):
    session_id: str


@router.post("/sessions/revoke")
async def revoke_session(body: RevokeSessionBody, request: Request):
    user = await get_current_user(request)
    ok = await revoke_session_by_id(user["_id"], body.session_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Session not found.")
    return {"message": "Session revoked."}


@router.post("/sessions/revoke-others")
async def revoke_other_sessions(request: Request):
    user = await get_current_user(request)
    current_refresh = request.cookies.get("refresh_token")
    current_sid = None
    if current_refresh:
        from security import _hash_token
        rec = await db.refresh_tokens.find_one({"token_hash": _hash_token(current_refresh)})
        if rec:
            current_sid = rec.get("session_id")
    n = await revoke_all_user_sessions(user["_id"], except_session_id=current_sid)
    return {"message": f"Revoked {n} other session(s)."}


# ============================================================
# Change password (revokes all other sessions)
# ============================================================
class ChangePasswordBody(BaseModel):
    current_password: str
    new_password: str


@router.post("/password/change")
async def change_password(body: ChangePasswordBody, request: Request):
    user = await get_current_user(request)
    fresh = await db.users.find_one({"_id": ObjectId(user["_id"])})
    if not fresh or not verify_password(body.current_password, fresh["password_hash"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    validate_password_strength(
        body.new_password,
        user_inputs=[fresh.get("email", ""), fresh.get("name", "")]
    )

    await db.users.update_one(
        {"_id": fresh["_id"]},
        {"$set": {
            "password_hash": hash_password(body.new_password),
            "password_changed_at": datetime.now(timezone.utc).isoformat(),
        }}
    )

    # Revoke other sessions, keep current
    current_refresh = request.cookies.get("refresh_token")
    current_sid = None
    if current_refresh:
        from security import _hash_token
        rec = await db.refresh_tokens.find_one({"token_hash": _hash_token(current_refresh)})
        if rec:
            current_sid = rec.get("session_id")
    await revoke_all_user_sessions(user["_id"], except_session_id=current_sid)

    return JSONResponse(content={"message": "Password changed. Other sessions have been signed out."})
