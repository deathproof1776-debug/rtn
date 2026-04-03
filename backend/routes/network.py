"""
Trade Network routes: connections, requests, recommendations.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone

from database import db, decrypt_data
from auth import get_current_user
from models import NetworkRequest, NetworkRequestResponse, get_item_names
from notifications import send_push_notification

router = APIRouter(prefix="/network")


@router.post("/request")
async def send_network_request(data: NetworkRequest, request: Request, background_tasks: BackgroundTasks):
    """Send a trade network request to another user"""
    user = await get_current_user(request)
    target_user_id = data.target_user_id

    if target_user_id == user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot send network request to yourself")

    target_user = await db.users.find_one({"_id": ObjectId(target_user_id)})
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_connection = await db.network_connections.find_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": target_user_id},
            {"user_id": target_user_id, "connected_user_id": user["_id"]}
        ]
    })
    if existing_connection:
        raise HTTPException(status_code=400, detail="Already in trade network")

    existing_request = await db.network_requests.find_one({
        "$or": [
            {"from_user_id": user["_id"], "to_user_id": target_user_id, "status": "pending"},
            {"from_user_id": target_user_id, "to_user_id": user["_id"], "status": "pending"}
        ]
    })
    if existing_request:
        raise HTTPException(status_code=400, detail="Network request already pending")

    request_doc = {
        "from_user_id": user["_id"],
        "from_user_name": user.get("name", "Unknown"),
        "from_user_avatar": user.get("avatar", ""),
        "to_user_id": target_user_id,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    result = await db.network_requests.insert_one(request_doc)

    background_tasks.add_task(
        send_push_notification,
        user_id=target_user_id,
        title="New Trade Network Request",
        body=f"{user.get('name', 'Someone')} wants to join your trade network",
        data={"type": "network_request", "from_user_id": user["_id"], "url": "/network"}
    )

    return {"id": str(result.inserted_id), "message": "Network request sent"}


@router.post("/respond")
async def respond_to_network_request(data: NetworkRequestResponse, request: Request, background_tasks: BackgroundTasks):
    """Accept or decline a network request"""
    user = await get_current_user(request)
    request_id = data.request_id

    network_request = await db.network_requests.find_one({
        "_id": ObjectId(request_id),
        "to_user_id": user["_id"],
        "status": "pending"
    })

    if not network_request:
        raise HTTPException(status_code=404, detail="Network request not found")

    from_user_id = network_request["from_user_id"]

    if data.accept:
        connection_doc = {
            "user_id": user["_id"],
            "connected_user_id": from_user_id,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        await db.network_connections.insert_one(connection_doc)

        await db.network_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "accepted", "responded_at": datetime.now(timezone.utc).isoformat()}}
        )

        background_tasks.add_task(
            send_push_notification,
            user_id=from_user_id,
            title="Network Request Accepted",
            body=f"{user.get('name', 'Someone')} accepted your trade network request",
            data={"type": "network_accepted", "user_id": user["_id"], "url": "/network"}
        )

        return {"message": "Network request accepted", "connected": True}
    else:
        await db.network_requests.update_one(
            {"_id": ObjectId(request_id)},
            {"$set": {"status": "declined", "responded_at": datetime.now(timezone.utc).isoformat()}}
        )
        return {"message": "Network request declined", "connected": False}


@router.get("/requests/pending")
async def get_pending_requests(request: Request):
    """Get pending network requests for current user"""
    user = await get_current_user(request)

    incoming = await db.network_requests.find({
        "to_user_id": user["_id"],
        "status": "pending"
    }).sort("created_at", -1).to_list(50)

    outgoing = await db.network_requests.find({
        "from_user_id": user["_id"],
        "status": "pending"
    }).sort("created_at", -1).to_list(50)

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


@router.get("/connections")
async def get_network_connections(request: Request):
    """Get all users in the current user's trade network"""
    user = await get_current_user(request)

    connections = await db.network_connections.find({
        "$or": [
            {"user_id": user["_id"]},
            {"connected_user_id": user["_id"]}
        ]
    }).to_list(500)

    connected_user_ids = set()
    for conn in connections:
        if conn["user_id"] == user["_id"]:
            connected_user_ids.add(conn["connected_user_id"])
        else:
            connected_user_ids.add(conn["user_id"])

    network_users = []
    for uid in connected_user_ids:
        u = await db.users.find_one({"_id": ObjectId(uid)}, {"password_hash": 0})
        if u:
            u["_id"] = str(u["_id"])
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


@router.delete("/connections/{user_id}")
async def remove_from_network(user_id: str, request: Request):
    """Remove a user from your trade network"""
    user = await get_current_user(request)

    result = await db.network_connections.delete_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": user_id},
            {"user_id": user_id, "connected_user_id": user["_id"]}
        ]
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {"message": "Removed from trade network"}


@router.get("/status/{user_id}")
async def get_network_status(user_id: str, request: Request):
    """Check network status with another user"""
    user = await get_current_user(request)

    connection = await db.network_connections.find_one({
        "$or": [
            {"user_id": user["_id"], "connected_user_id": user_id},
            {"user_id": user_id, "connected_user_id": user["_id"]}
        ]
    })

    if connection:
        return {"status": "connected", "can_request": False}

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


@router.post("/cancel/{request_id}")
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


def _build_match_reason(offers_match: set, wants_match: set) -> str:
    """Build a human-readable match reason"""
    reasons = []
    if offers_match:
        items = list(offers_match)[:2]
        if len(items) == 1:
            reasons.append(f"Offers {items[0]}")
        else:
            reasons.append(f"Offers {items[0]}, {items[1]}")
    if wants_match:
        items = list(wants_match)[:2]
        if len(items) == 1:
            reasons.append(f"Wants {items[0]}")
        else:
            reasons.append(f"Wants {items[0]}, {items[1]}")
    return " • ".join(reasons) if reasons else "Potential match"


@router.get("/recommended")
async def get_recommended_traders(request: Request, limit: int = 10):
    """Get recommended traders based on complementary goods/services matching"""
    user = await get_current_user(request)
    user_doc = await db.users.find_one({"_id": ObjectId(user["_id"])})

    # Use get_item_names to extract names from items (which may be dicts or strings)
    user_goods_wanted = set(get_item_names(user_doc.get("goods_wanted", [])))
    user_services_wanted = set(get_item_names(user_doc.get("services_wanted", [])))
    user_goods_offering = set(get_item_names(user_doc.get("goods_offering", [])))
    user_services_offering = set(get_item_names(user_doc.get("services_offering", [])))

    all_user_wants = user_goods_wanted | user_services_wanted
    all_user_offerings = user_goods_offering | user_services_offering

    if not all_user_wants and not all_user_offerings:
        return {
            "recommendations": [],
            "message": "Update your profile with goods/services you're offering and looking for to get recommendations"
        }

    connections = await db.network_connections.find({
        "$or": [
            {"user_id": user["_id"]},
            {"connected_user_id": user["_id"]}
        ]
    }).to_list(500)

    connected_ids = set()
    for conn in connections:
        if conn["user_id"] == user["_id"]:
            connected_ids.add(conn["connected_user_id"])
        else:
            connected_ids.add(conn["user_id"])

    pending_requests = await db.network_requests.find({
        "$or": [
            {"from_user_id": user["_id"], "status": "pending"},
            {"to_user_id": user["_id"], "status": "pending"}
        ]
    }).to_list(100)

    pending_ids = set()
    for req in pending_requests:
        if req["from_user_id"] == user["_id"]:
            pending_ids.add(req["to_user_id"])
        else:
            pending_ids.add(req["from_user_id"])

    exclude_ids = connected_ids | pending_ids | {user["_id"]}
    all_users = await db.users.find(
        {"_id": {"$nin": [ObjectId(uid) for uid in exclude_ids]}},
        {"password_hash": 0}
    ).limit(100).to_list(100)

    recommendations = []
    for u in all_users:
        u_id = str(u["_id"])
        # Use get_item_names to extract names from items (which may be dicts or strings)
        u_goods_offering = set(get_item_names(u.get("goods_offering", [])))
        u_services_offering = set(get_item_names(u.get("services_offering", [])))
        u_goods_wanted = set(get_item_names(u.get("goods_wanted", [])))
        u_services_wanted = set(get_item_names(u.get("services_wanted", [])))

        all_u_offerings = u_goods_offering | u_services_offering
        all_u_wants = u_goods_wanted | u_services_wanted

        offers_match = all_user_wants & all_u_offerings
        wants_match = all_user_offerings & all_u_wants

        if not offers_match and not wants_match:
            continue

        score = len(offers_match) * 15 + len(wants_match) * 10

        location = ""
        if u.get("location"):
            try:
                location = decrypt_data(u["location"])
            except Exception:
                location = u.get("location", "")

        recommendations.append({
            "id": u_id,
            "name": u.get("name", "Unknown"),
            "avatar": u.get("avatar", ""),
            "location": location,
            "is_verified": u.get("is_verified", False),
            "skills": u.get("skills", [])[:3],
            "match_score": score,
            "offers_you_want": list(offers_match)[:5],
            "wants_you_offer": list(wants_match)[:5],
            "reason": _build_match_reason(offers_match, wants_match)
        })

    recommendations.sort(key=lambda x: -x["match_score"])

    return {
        "recommendations": recommendations[:limit],
        "total_matches": len(recommendations)
    }
