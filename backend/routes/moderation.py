"""
Moderation routes: user block/unblock and content reporting.
"""
from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId
from datetime import datetime, timezone

from database import db
from auth import get_current_user, require_moderator
from moderation_utils import get_blocked_user_ids
from security import limiter, user_rate_limit_key

router = APIRouter(prefix="/moderation")

VALID_REPORT_TARGETS = {"user", "post", "comment", "community_post", "gallery_item"}
VALID_REPORT_REASONS = {
    "spam", "harassment", "hate_speech", "nsfw",
    "scam", "impersonation", "violence", "other"
}


# ----------------------- Blocks -----------------------

@router.post("/block/{user_id}", status_code=201)
async def block_user(user_id: str, request: Request):
    """Block a user. Hides their content from current user and vice versa."""
    me = await get_current_user(request)
    if user_id == me["_id"]:
        raise HTTPException(status_code=400, detail="Cannot block yourself")

    # Validate the target user exists
    try:
        target = await db.users.find_one({"_id": ObjectId(user_id)}, {"_id": 1})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user id")
    if not target:
        raise HTTPException(status_code=404, detail="User not found")

    existing = await db.blocks.find_one({"blocker_id": me["_id"], "blocked_id": user_id})
    if existing:
        return {"message": "User already blocked"}

    await db.blocks.insert_one({
        "blocker_id": me["_id"],
        "blocked_id": user_id,
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    return {"message": "User blocked"}


@router.delete("/block/{user_id}")
async def unblock_user(user_id: str, request: Request):
    """Unblock a previously blocked user."""
    me = await get_current_user(request)
    result = await db.blocks.delete_one({"blocker_id": me["_id"], "blocked_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Block not found")
    return {"message": "User unblocked"}


@router.get("/blocks")
async def list_my_blocks(request: Request):
    """List users the current user has blocked."""
    me = await get_current_user(request)
    cursor = db.blocks.find(
        {"blocker_id": me["_id"]},
        {"_id": 0, "blocked_id": 1, "created_at": 1}
    ).sort("created_at", -1)

    rows = await cursor.to_list(500)
    blocked_ids = [r["blocked_id"] for r in rows]
    if not blocked_ids:
        return {"blocks": []}

    users_cursor = db.users.find(
        {"_id": {"$in": [ObjectId(uid) for uid in blocked_ids if ObjectId.is_valid(uid)]}},
        {"_id": 1, "name": 1, "avatar": 1}
    )
    users_map = {}
    async for u in users_cursor:
        users_map[str(u["_id"])] = {
            "name": u.get("name", "Unknown"),
            "avatar": u.get("avatar", "")
        }

    return {
        "blocks": [
            {
                "user_id": r["blocked_id"],
                "name": users_map.get(r["blocked_id"], {}).get("name", "Unknown user"),
                "avatar": users_map.get(r["blocked_id"], {}).get("avatar", ""),
                "blocked_at": r["created_at"]
            }
            for r in rows
        ]
    }


@router.get("/blocks/check/{user_id}")
async def check_block(user_id: str, request: Request):
    """Check whether the current user has blocked or is blocked by user_id."""
    me = await get_current_user(request)
    blocked = await get_blocked_user_ids(me["_id"])
    i_blocked = await db.blocks.find_one({"blocker_id": me["_id"], "blocked_id": user_id})
    return {
        "is_blocked_either_way": user_id in blocked,
        "i_blocked_them": i_blocked is not None
    }


# ----------------------- Reports -----------------------

@router.post("/report", status_code=201)
@limiter.limit("10/hour", key_func=user_rate_limit_key)
async def submit_report(request: Request):
    """Submit a report against a user or piece of content."""
    me = await get_current_user(request)
    data = await request.json()

    target_type = (data.get("target_type") or "").strip()
    target_id = (data.get("target_id") or "").strip()
    reason = (data.get("reason") or "").strip()
    details = (data.get("details") or "").strip()[:1000]

    if target_type not in VALID_REPORT_TARGETS:
        raise HTTPException(status_code=400, detail="Invalid target_type")
    if not target_id:
        raise HTTPException(status_code=400, detail="target_id is required")
    if reason not in VALID_REPORT_REASONS:
        raise HTTPException(status_code=400, detail="Invalid reason")

    # Prevent duplicate pending reports from the same user on the same target
    duplicate = await db.reports.find_one({
        "reporter_id": me["_id"],
        "target_type": target_type,
        "target_id": target_id,
        "status": "pending"
    })
    if duplicate:
        return {"message": "Report already submitted, awaiting review"}

    await db.reports.insert_one({
        "reporter_id": me["_id"],
        "reporter_name": me.get("name", "Anonymous"),
        "target_type": target_type,
        "target_id": target_id,
        "reason": reason,
        "details": details,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resolved_at": None,
        "resolved_by": None,
        "resolution_note": None
    })
    return {"message": "Report submitted"}


# ----------------------- Admin / Moderator -----------------------

admin_router = APIRouter(prefix="/admin")


async def _log_mod_action(actor: dict, action: str, report_id: str, note: str = ""):
    await db.audit_log.insert_one({
        "admin_id": actor["_id"],
        "admin_name": actor.get("name", "Staff"),
        "action": action,
        "target_type": "report",
        "target_id": report_id,
        "target_name": f"report {report_id}",
        "details": note,
        "created_at": datetime.now(timezone.utc).isoformat(),
    })


@admin_router.get("/reports")
async def list_reports(request: Request, status: str = "pending", limit: int = 100):
    """Moderator/Admin: list reports filtered by status."""
    await require_moderator(request)

    valid_status = {"pending", "resolved", "dismissed", "escalated", "all"}
    if status not in valid_status:
        raise HTTPException(status_code=400, detail="Invalid status filter")

    if status == "all":
        query = {}
    elif status == "escalated":
        query = {"escalated": True}
    else:
        query = {"status": status}
    cursor = db.reports.find(query).sort("created_at", -1).limit(limit)

    reports = []
    async for r in cursor:
        reports.append({
            "_id": str(r["_id"]),
            "reporter_id": r.get("reporter_id"),
            "reporter_name": r.get("reporter_name"),
            "target_type": r.get("target_type"),
            "target_id": r.get("target_id"),
            "reason": r.get("reason"),
            "details": r.get("details", ""),
            "status": r.get("status"),
            "escalated": bool(r.get("escalated", False)),
            "escalated_by_name": r.get("escalated_by_name"),
            "created_at": r.get("created_at"),
            "resolved_at": r.get("resolved_at"),
            "resolved_by_name": r.get("resolved_by_name"),
            "resolution_note": r.get("resolution_note")
        })
    return {"reports": reports}


@admin_router.put("/reports/{report_id}")
async def update_report(report_id: str, request: Request):
    """Moderator/Admin: resolve or dismiss a report.

    Once a report is escalated, only an admin may resolve/dismiss it.
    """
    actor = await require_moderator(request)
    data = await request.json()
    new_status = (data.get("status") or "").strip()
    note = (data.get("resolution_note") or "").strip()[:500]

    if new_status not in {"resolved", "dismissed", "pending"}:
        raise HTTPException(status_code=400, detail="Invalid status")

    try:
        oid = ObjectId(report_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report id")

    report = await db.reports.find_one({"_id": oid})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.get("escalated") and actor.get("role") != "admin":
        raise HTTPException(
            status_code=403,
            detail="This report has been escalated and can only be actioned by an admin."
        )

    update_doc = {
        "status": new_status,
        "resolution_note": note or None,
        "resolved_at": datetime.now(timezone.utc).isoformat() if new_status != "pending" else None,
        "resolved_by": actor["_id"] if new_status != "pending" else None,
        "resolved_by_name": actor.get("name") if new_status != "pending" else None,
    }
    await db.reports.update_one({"_id": oid}, {"$set": update_doc})
    await _log_mod_action(actor, f"report_{new_status}", report_id, note)
    return {"message": "Report updated"}


@admin_router.put("/reports/{report_id}/escalate")
async def escalate_report(report_id: str, request: Request):
    """Moderator/Admin: escalate a report to admin attention."""
    actor = await require_moderator(request)
    try:
        oid = ObjectId(report_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid report id")

    result = await db.reports.update_one(
        {"_id": oid},
        {"$set": {
            "escalated": True,
            "escalated_by": actor["_id"],
            "escalated_by_name": actor.get("name", "Moderator"),
            "escalated_at": datetime.now(timezone.utc).isoformat(),
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Report not found")
    await _log_mod_action(actor, "report_escalated", report_id)
    return {"message": "Report escalated to admin"}


@admin_router.get("/reports/stats")
async def report_stats(request: Request):
    """Moderator/Admin: report counts for dashboard badges."""
    await require_moderator(request)
    pending = await db.reports.count_documents({"status": "pending"})
    resolved = await db.reports.count_documents({"status": "resolved"})
    dismissed = await db.reports.count_documents({"status": "dismissed"})
    escalated = await db.reports.count_documents({"escalated": True, "status": "pending"})
    return {"pending": pending, "resolved": resolved, "dismissed": dismissed, "escalated": escalated}
