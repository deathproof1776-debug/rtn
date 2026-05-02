"""
Security utilities: rate limiting, account lockout, password strength,
TOTP (2FA), recovery codes, and refresh-token rotation/revocation.
"""
import os
import hashlib
import secrets
import base64
from datetime import datetime, timezone, timedelta
from io import BytesIO
from typing import Optional

import bcrypt
import jwt
import pyotp
import qrcode
from zxcvbn import zxcvbn
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import HTTPException, Request

from database import db


# ============================================================
# Rate limiting (in-memory; Redis not required)
# ============================================================
limiter = Limiter(key_func=get_remote_address, default_limits=[])


# ============================================================
# Account lockout
# ============================================================
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_MINUTES = 15


def _ip_from_request(request: Request) -> str:
    fwd = request.headers.get("x-forwarded-for")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def check_lockout(request: Request, email: str) -> None:
    """Raise 429 if this email is currently locked out from logging in."""
    record = await db.login_attempts.find_one({"email": email})
    if not record:
        return
    locked_until = record.get("locked_until")
    if locked_until:
        try:
            dt = datetime.fromisoformat(locked_until)
        except Exception:
            return
        if dt > datetime.now(timezone.utc):
            mins = max(1, int((dt - datetime.now(timezone.utc)).total_seconds() / 60))
            raise HTTPException(
                status_code=429,
                detail=f"Account temporarily locked due to too many failed login attempts. Try again in {mins} minute(s)."
            )


async def record_failed_attempt(request: Request, email: str) -> None:
    """Increment failed attempts; lock for LOCKOUT_MINUTES at MAX_FAILED_ATTEMPTS."""
    now = datetime.now(timezone.utc)
    record = await db.login_attempts.find_one({"email": email}) or {}
    count = int(record.get("count", 0)) + 1
    update = {
        "email": email,
        "ip": _ip_from_request(request),
        "count": count,
        "last_attempt": now.isoformat(),
    }
    if count >= MAX_FAILED_ATTEMPTS:
        update["locked_until"] = (now + timedelta(minutes=LOCKOUT_MINUTES)).isoformat()
        update["count"] = 0  # reset window after locking
    await db.login_attempts.update_one(
        {"email": email}, {"$set": update}, upsert=True
    )


async def clear_failed_attempts(email: str) -> None:
    await db.login_attempts.delete_one({"email": email})


# ============================================================
# Password strength (zxcvbn) — minimum score 2 (out of 4)
# ============================================================
MIN_PASSWORD_SCORE = 2
MIN_PASSWORD_LENGTH = 8


def validate_password_strength(password: str, user_inputs: Optional[list] = None) -> None:
    """Raise 400 if password is too weak."""
    if not password or len(password) < MIN_PASSWORD_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Password must be at least {MIN_PASSWORD_LENGTH} characters."
        )
    result = zxcvbn(password, user_inputs=user_inputs or [])
    score = result.get("score", 0)
    if score < MIN_PASSWORD_SCORE:
        feedback = result.get("feedback") or {}
        warning = feedback.get("warning") or "Password is too weak or commonly used."
        suggestions = feedback.get("suggestions") or []
        msg = warning
        if suggestions:
            msg += " " + " ".join(suggestions)
        raise HTTPException(status_code=400, detail=msg)


# ============================================================
# TOTP / 2FA helpers
# ============================================================
TOTP_ISSUER = "Rebel Trade Network"


def generate_totp_secret() -> str:
    return pyotp.random_base32()


def totp_provisioning_uri(secret: str, account_name: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(
        name=account_name, issuer_name=TOTP_ISSUER
    )


def totp_qr_data_url(uri: str) -> str:
    img = qrcode.make(uri)
    buf = BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def verify_totp(secret: str, code: str) -> bool:
    if not secret or not code:
        return False
    return pyotp.TOTP(secret).verify(code.strip(), valid_window=1)


# ---- Recovery codes ----
RECOVERY_CODE_COUNT = 8


def _hash_code(code: str) -> str:
    return bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_code(code: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(code.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def generate_recovery_codes() -> list:
    """Returns plaintext codes (shown once). Caller must hash before storing."""
    codes = []
    for _ in range(RECOVERY_CODE_COUNT):
        raw = secrets.token_hex(5).upper()  # 10 hex chars
        codes.append(f"{raw[:5]}-{raw[5:]}")
    return codes


async def store_recovery_codes(user_id: str, plain_codes: list) -> None:
    await db.recovery_codes.delete_many({"user_id": user_id})
    docs = [
        {"user_id": user_id, "code_hash": _hash_code(c), "used": False,
         "created_at": datetime.now(timezone.utc).isoformat()}
        for c in plain_codes
    ]
    if docs:
        await db.recovery_codes.insert_many(docs)


async def consume_recovery_code(user_id: str, code: str) -> bool:
    if not code:
        return False
    code = code.strip().upper()
    items = await db.recovery_codes.find({"user_id": user_id, "used": False}).to_list(50)
    for item in items:
        if _verify_code(code, item["code_hash"]):
            await db.recovery_codes.update_one(
                {"_id": item["_id"]},
                {"$set": {"used": True, "used_at": datetime.now(timezone.utc).isoformat()}}
            )
            return True
    return False


# ============================================================
# 2FA challenge tokens (short-lived, signed JWT)
# ============================================================
def create_2fa_challenge_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "type": "2fa_challenge",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
    }
    return jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")


def decode_2fa_challenge_token(token: str) -> str:
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="2FA challenge expired. Please log in again.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid 2FA challenge token.")
    if payload.get("type") != "2fa_challenge":
        raise HTTPException(status_code=401, detail="Invalid 2FA challenge token.")
    return payload["sub"]


# ============================================================
# Refresh token storage (so we can revoke / log out everywhere)
# ============================================================
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def store_refresh_token(
    user_id: str, refresh_token: str, request: Request,
    session_id: Optional[str] = None, expires_in_days: int = 7,
) -> str:
    """Store the refresh token's hash; returns session_id."""
    if not session_id:
        session_id = secrets.token_urlsafe(16)
    await db.refresh_tokens.insert_one({
        "session_id": session_id,
        "user_id": user_id,
        "token_hash": _hash_token(refresh_token),
        "user_agent": request.headers.get("user-agent", "")[:300],
        "ip": _ip_from_request(request),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat(),
        "revoked": False,
        "last_used_at": datetime.now(timezone.utc).isoformat(),
    })
    return session_id


async def find_refresh_token(refresh_token: str) -> Optional[dict]:
    return await db.refresh_tokens.find_one({
        "token_hash": _hash_token(refresh_token), "revoked": False
    })


async def rotate_refresh_token(old_token: str, new_token: str) -> None:
    await db.refresh_tokens.update_one(
        {"token_hash": _hash_token(old_token)},
        {"$set": {
            "token_hash": _hash_token(new_token),
            "last_used_at": datetime.now(timezone.utc).isoformat(),
        }}
    )


async def revoke_refresh_token(refresh_token: str) -> None:
    await db.refresh_tokens.update_one(
        {"token_hash": _hash_token(refresh_token)},
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
    )


async def revoke_all_user_sessions(user_id: str, except_session_id: Optional[str] = None) -> int:
    query = {"user_id": user_id, "revoked": False}
    if except_session_id:
        query["session_id"] = {"$ne": except_session_id}
    res = await db.refresh_tokens.update_many(
        query,
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
    )
    return res.modified_count


async def revoke_session_by_id(user_id: str, session_id: str) -> bool:
    res = await db.refresh_tokens.update_one(
        {"user_id": user_id, "session_id": session_id, "revoked": False},
        {"$set": {"revoked": True, "revoked_at": datetime.now(timezone.utc).isoformat()}}
    )
    return res.modified_count > 0
