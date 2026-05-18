"""
Moderation utilities: block-list helpers shared across feed/messaging routes.
"""
from database import db


async def get_blocked_user_ids(user_id: str) -> set:
    """Return the set of user_ids that the current user has blocked OR
    that have blocked the current user (mutual hiding model)."""
    if not user_id:
        return set()

    cursor = db.blocks.find(
        {"$or": [{"blocker_id": user_id}, {"blocked_id": user_id}]},
        {"_id": 0, "blocker_id": 1, "blocked_id": 1}
    )
    blocked = set()
    async for doc in cursor:
        # Add the "other" side of the relationship
        other = doc["blocked_id"] if doc["blocker_id"] == user_id else doc["blocker_id"]
        blocked.add(other)
    return blocked


async def is_blocked_between(user_a: str, user_b: str) -> bool:
    """Return True if either user has blocked the other."""
    if not user_a or not user_b or user_a == user_b:
        return False
    doc = await db.blocks.find_one({
        "$or": [
            {"blocker_id": user_a, "blocked_id": user_b},
            {"blocker_id": user_b, "blocked_id": user_a}
        ]
    })
    return doc is not None
