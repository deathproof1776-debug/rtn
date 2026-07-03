"""
Achievements / milestone celebrations.

Grants a one-time in-app celebration (queued on the user doc as
`pending_achievements`) plus a push notification when a user earns a badge
or role. The frontend shows a celebration modal and then acknowledges it.
"""
from bson import ObjectId

from database import db
from notifications import send_push_notification

# key -> push notification copy + deep link
ACHIEVEMENTS = {
    "verified": {
        "push_title": "You're a Verified Trader! ✓",
        "push_body": "Your account has been verified. You can now invite new members.",
        "url": "/",
    },
    "trusted_trader": {
        "push_title": "Trusted Trader Unlocked! 🤝",
        "push_body": "You've completed 5 trades. You've earned the Trusted Trader badge.",
        "url": "/",
    },
    "moderator": {
        "push_title": "You're now a Moderator 🛡",
        "push_body": "You can review community reports and keep the network safe.",
        "url": "/",
    },
}


async def grant_achievement(user_id: str, key: str) -> None:
    """Queue a one-time celebration for `key` and fire a push notification.

    Idempotent: adding an already-pending key via $addToSet is a no-op.
    """
    meta = ACHIEVEMENTS.get(key)
    if not meta or not ObjectId.is_valid(user_id):
        return
    await db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$addToSet": {"pending_achievements": key}}
    )
    try:
        await send_push_notification(
            user_id=user_id,
            title=meta["push_title"],
            body=meta["push_body"],
            data={"type": "achievement", "key": key, "url": meta.get("url", "/")},
        )
    except Exception:
        pass


def qualifying_achievement_keys(user: dict) -> set:
    """Achievement keys the user currently qualifies for based on their status."""
    keys = set()
    if user.get("is_verified"):
        keys.add("verified")
    if user.get("is_trusted_trader"):
        keys.add("trusted_trader")
    if user.get("role") == "moderator":
        keys.add("moderator")
    return keys


async def backfill_pending_achievements(user_id: str, user: dict) -> list:
    """Ensure existing users receive explainers for badges/roles they already
    hold but never saw. Adds any qualifying key not already pending or seen.

    Called lazily on login/`/me`, so it self-heals for all existing users on
    their next session and never re-shows an acknowledged achievement.
    """
    seen = set(user.get("achievements_seen") or [])
    pending = list(user.get("pending_achievements") or [])
    pending_set = set(pending)
    to_add = [k for k in qualifying_achievement_keys(user)
              if k not in seen and k not in pending_set]
    if to_add and ObjectId.is_valid(user_id):
        await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$addToSet": {"pending_achievements": {"$each": to_add}}}
        )
        pending = pending + to_add
    return pending
