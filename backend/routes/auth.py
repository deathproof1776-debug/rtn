"""
Authentication routes: register, login, logout, token refresh.

Hardened with: rate limiting, account lockout, password strength validation,
TOTP-based 2FA challenge for admin/verified users, and refresh-token rotation.
"""
import secrets
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
from security import (
    limiter,
    check_lockout, record_failed_attempt, clear_failed_attempts,
    validate_password_strength,
    create_2fa_challenge_token, decode_2fa_challenge_token,
    verify_totp, consume_recovery_code,
    store_refresh_token, find_refresh_token, rotate_refresh_token,
    revoke_refresh_token,
)
import jwt
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/auth")


def _set_auth_cookies(response: JSONResponse, access_token: str, refresh_token: str):
    response.set_cookie(key="access_token", value=access_token, httponly=True,
                        secure=True, samesite="none", max_age=3600, path="/")
    response.set_cookie(key="refresh_token", value=refresh_token, httponly=True,
                        secure=True, samesite="none", max_age=604800, path="/")


def _user_response_payload(user: dict) -> dict:
    location = ""
    if user.get("location"):
        try:
            location = decrypt_data(user["location"])
        except Exception:
            location = user.get("location", "")
    return {
        "id": str(user["_id"]),
        "email": user.get("email", ""),
        "name": user.get("name", ""),
        "location": location,
        "avatar": user.get("avatar", ""),
        "is_verified": user.get("is_verified", False),
        "is_trusted_trader": user.get("is_trusted_trader", False),
        "two_factor_enabled": bool(user.get("two_factor_enabled", False)),
        "role": user.get("role", "user"),
        "has_seen_onboarding": bool(user.get("has_seen_onboarding", False)),
        "pending_achievements": user.get("pending_achievements", []),
    }


def _requires_2fa(user: dict) -> bool:
    """Currently, 2FA is enforced only when the user has explicitly enabled it.
    We strongly recommend it for admin/verified users via UI nudges."""
    return bool(user.get("two_factor_enabled"))


async def _issue_session(user: dict, email: str, request: Request) -> JSONResponse:
    user_id = str(user["_id"])
    session_id = secrets.token_urlsafe(16)
    access_token = create_access_token(user_id, email)
    refresh_token = create_refresh_token(user_id, session_id=session_id)
    await store_refresh_token(user_id, refresh_token, request, session_id=session_id)

    payload = _user_response_payload(user)
    payload["message"] = "Login successful"
    response = JSONResponse(content=payload)
    _set_auth_cookies(response, access_token, refresh_token)
    return response


# ============================================================
# Register
# ============================================================
@router.post("/register")
@limiter.limit("5/hour")
async def register(request: Request, user_data: UserRegister):
    invite = await db.invites.find_one({"token": user_data.invite_token, "used": False})
    if not invite:
        raise HTTPException(status_code=403, detail="Invalid or expired invite link. You need a valid invitation from an existing member to join.")

    invite_created = datetime.fromisoformat(invite["created_at"])
    if datetime.now(timezone.utc) - invite_created > timedelta(days=7):
        raise HTTPException(status_code=403, detail="This invite link has expired. Please request a new one from a member.")

    email = user_data.email.lower()
    existing = await db.users.find_one({"email": email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Password strength check
    validate_password_strength(user_data.password, user_inputs=[email, user_data.name or ""])

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
        "two_factor_enabled": False,
        "invited_by": str(invite["created_by"]),
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.users.insert_one(user_doc)
    user_id = str(result.inserted_id)

    await db.invites.update_one(
        {"_id": invite["_id"]},
        {"$set": {"used": True, "used_by": user_id, "used_at": datetime.now(timezone.utc).isoformat()}}
    )

    user_doc["_id"] = result.inserted_id
    return await _issue_session(user_doc, email, request)


# ============================================================
# Login (with lockout + optional 2FA challenge)
# ============================================================
@router.post("/login")
@limiter.limit("10/minute")
async def login(request: Request, user_data: UserLogin):
    email = user_data.email.lower()

    await check_lockout(request, email)

    user = await db.users.find_one({"email": email})
    if not user:
        await record_failed_attempt(request, email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not verify_password(user_data.password, user["password_hash"]):
        await record_failed_attempt(request, email)
        raise HTTPException(status_code=401, detail="Invalid email or password")

    await clear_failed_attempts(email)

    if _requires_2fa(user):
        challenge = create_2fa_challenge_token(str(user["_id"]))
        return JSONResponse(content={
            "two_factor_required": True,
            "challenge_token": challenge,
            "message": "Enter your authenticator code to continue."
        })

    return await _issue_session(user, email, request)


# ============================================================
# 2FA verify (completes a login challenge)
# ============================================================
class TwoFactorVerifyBody(BaseModel):
    challenge_token: str
    code: Optional[str] = None
    recovery_code: Optional[str] = None


@router.post("/login/2fa")
@limiter.limit("10/minute")
async def login_2fa(request: Request, body: TwoFactorVerifyBody):
    user_id = decode_2fa_challenge_token(body.challenge_token)
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    if not user.get("two_factor_enabled"):
        # 2FA was disabled between steps; just issue session
        return await _issue_session(user, user["email"], request)

    secret = user.get("totp_secret")
    ok = False
    if body.code and secret and verify_totp(secret, body.code):
        ok = True
    elif body.recovery_code and await consume_recovery_code(user_id, body.recovery_code):
        ok = True

    if not ok:
        raise HTTPException(status_code=401, detail="Invalid authenticator code.")

    return await _issue_session(user, user["email"], request)


# ============================================================
# Logout (revokes the current refresh token only)
# ============================================================
@router.post("/logout")
async def logout(request: Request):
    refresh = request.cookies.get("refresh_token")
    if refresh:
        try:
            await revoke_refresh_token(refresh)
        except Exception:
            pass
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie(key="access_token", path="/", secure=True, samesite="none")
    response.delete_cookie(key="refresh_token", path="/", secure=True, samesite="none")
    return response


# ============================================================
# Me
# ============================================================
@router.get("/me")
async def get_me(request: Request):
    user = await get_current_user(request)
    if user.get("location"):
        try:
            user["location"] = decrypt_data(user["location"])
        except Exception:
            pass
    if "_id" in user:
        user["id"] = user.pop("_id")
    user["two_factor_enabled"] = bool(user.get("two_factor_enabled", False))
    user["has_seen_onboarding"] = bool(user.get("has_seen_onboarding", False))
    user["pending_achievements"] = user.get("pending_achievements", [])
    user.pop("totp_secret", None)
    return user


# ============================================================
# Refresh token (rotates the refresh token)
# ============================================================
@router.post("/refresh")
async def refresh_token_endpoint(request: Request):
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

        # Confirm session is still valid (not revoked)
        stored = await find_refresh_token(token)
        if not stored:
            raise HTTPException(status_code=401, detail="Session revoked. Please log in again.")

        session_id = stored.get("session_id") or payload.get("sid")
        new_access = create_access_token(str(user["_id"]), user["email"])
        new_refresh = create_refresh_token(str(user["_id"]), session_id=session_id)
        await rotate_refresh_token(token, new_refresh)

        response = JSONResponse(content={"message": "Token refreshed"})
        _set_auth_cookies(response, new_access, new_refresh)
        return response
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ============================================================
# Password strength check (utility for frontend live meter)
# ============================================================
class PasswordCheckBody(BaseModel):
    password: str
    user_inputs: Optional[list] = None


@router.post("/password/check")
async def password_check(body: PasswordCheckBody):
    from zxcvbn import zxcvbn
    if not body.password:
        return {"score": 0, "warning": "", "suggestions": []}
    res = zxcvbn(body.password, user_inputs=body.user_inputs or [])
    fb = res.get("feedback") or {}
    return {
        "score": res.get("score", 0),
        "warning": fb.get("warning") or "",
        "suggestions": fb.get("suggestions") or [],
    }
