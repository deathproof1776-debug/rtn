"""
Trade Deals routes: create offers, counter-offers, accept/decline.
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from bson import ObjectId
from datetime import datetime, timezone

from database import db, encrypt_data, decrypt_data
from auth import get_current_user
from models import TradeOfferCreate, TradeOfferRespond, TradeCounterOffer
from notifications import send_push_notification
from websocket_manager import manager

router = APIRouter(prefix="/trades")


@router.post("", status_code=201)
async def create_trade_offer(data: TradeOfferCreate, request: Request, background_tasks: BackgroundTasks):
    """Create a new trade offer/proposal"""
    user = await get_current_user(request)

    if data.receiver_id == user["_id"]:
        raise HTTPException(status_code=400, detail="Cannot create a trade offer with yourself")

    receiver = await db.users.find_one({"_id": ObjectId(data.receiver_id)}, {"name": 1})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver not found")

    if not data.offering or not data.requesting:
        raise HTTPException(status_code=400, detail="Both offering and requesting items are required")

    trade_doc = {
        "proposer_id": user["_id"],
        "proposer_name": user.get("name", "Unknown"),
        "receiver_id": data.receiver_id,
        "receiver_name": receiver.get("name", "Unknown"),
        "offering": data.offering,
        "requesting": data.requesting,
        "message": encrypt_data(data.message) if data.message else "",
        "status": "pending",
        "counter_offers": [],
        "post_id": data.post_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None
    }
    result = await db.trade_deals.insert_one(trade_doc)

    background_tasks.add_task(
        send_push_notification,
        user_id=data.receiver_id,
        title=f"New trade offer from {user.get('name', 'Someone')}",
        body=f"Offering: {', '.join(data.offering[:2])}",
        data={"type": "trade_offer", "trade_id": str(result.inserted_id), "url": "/"}
    )

    await manager.send_personal_message({
        "type": "trade_offer",
        "trade_id": str(result.inserted_id),
        "proposer_name": user.get("name", "Unknown"),
        "offering": data.offering,
        "requesting": data.requesting
    }, data.receiver_id)

    return {"id": str(result.inserted_id), "message": "Trade offer sent successfully"}


@router.get("/incoming")
async def get_incoming_trades(request: Request):
    """Get trade offers received by the current user"""
    user = await get_current_user(request)

    trades = await db.trade_deals.find(
        {"receiver_id": user["_id"], "status": {"$in": ["pending", "countered"]}},
        {"_id": 1, "proposer_id": 1, "proposer_name": 1, "receiver_id": 1, "receiver_name": 1,
         "offering": 1, "requesting": 1, "message": 1, "status": 1, "counter_offers": 1,
         "post_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(50)

    for trade in trades:
        trade["_id"] = str(trade["_id"])
        if trade.get("message"):
            try:
                trade["message"] = decrypt_data(trade["message"])
            except Exception:
                pass
        for co in trade.get("counter_offers", []):
            if co.get("message"):
                try:
                    co["message"] = decrypt_data(co["message"])
                except Exception:
                    pass

    return trades


@router.get("/outgoing")
async def get_outgoing_trades(request: Request):
    """Get trade offers sent by the current user"""
    user = await get_current_user(request)

    trades = await db.trade_deals.find(
        {"proposer_id": user["_id"], "status": {"$in": ["pending", "countered"]}},
        {"_id": 1, "proposer_id": 1, "proposer_name": 1, "receiver_id": 1, "receiver_name": 1,
         "offering": 1, "requesting": 1, "message": 1, "status": 1, "counter_offers": 1,
         "post_id": 1, "created_at": 1, "updated_at": 1}
    ).sort("updated_at", -1).to_list(50)

    for trade in trades:
        trade["_id"] = str(trade["_id"])
        if trade.get("message"):
            try:
                trade["message"] = decrypt_data(trade["message"])
            except Exception:
                pass
        for co in trade.get("counter_offers", []):
            if co.get("message"):
                try:
                    co["message"] = decrypt_data(co["message"])
                except Exception:
                    pass

    return trades


@router.get("/history")
async def get_trade_history(request: Request, skip: int = 0, limit: int = 50):
    """Get completed/declined/cancelled trade history"""
    user = await get_current_user(request)

    trades = await db.trade_deals.find(
        {
            "$or": [
                {"proposer_id": user["_id"]},
                {"receiver_id": user["_id"]}
            ],
            "status": {"$in": ["accepted", "declined", "cancelled"]}
        },
        {"_id": 1, "proposer_id": 1, "proposer_name": 1, "receiver_id": 1, "receiver_name": 1,
         "offering": 1, "requesting": 1, "message": 1, "status": 1, "counter_offers": 1,
         "post_id": 1, "created_at": 1, "updated_at": 1, "completed_at": 1}
    ).sort("updated_at", -1).skip(skip).limit(limit).to_list(limit)

    for trade in trades:
        trade["_id"] = str(trade["_id"])
        if trade.get("message"):
            try:
                trade["message"] = decrypt_data(trade["message"])
            except Exception:
                pass
        for co in trade.get("counter_offers", []):
            if co.get("message"):
                try:
                    co["message"] = decrypt_data(co["message"])
                except Exception:
                    pass

    total = await db.trade_deals.count_documents({
        "$or": [{"proposer_id": user["_id"]}, {"receiver_id": user["_id"]}],
        "status": {"$in": ["accepted", "declined", "cancelled"]}
    })

    return {"trades": trades, "total": total}


@router.get("/active-count")
async def get_active_trade_count(request: Request):
    """Get count of active incoming trade offers for badge display"""
    user = await get_current_user(request)
    count = await db.trade_deals.count_documents({
        "receiver_id": user["_id"],
        "status": {"$in": ["pending", "countered"]}
    })
    return {"count": count}


@router.post("/{trade_id}/respond")
async def respond_to_trade(trade_id: str, data: TradeOfferRespond, request: Request, background_tasks: BackgroundTasks):
    """Accept or decline a trade offer"""
    user = await get_current_user(request)

    trade = await db.trade_deals.find_one({"_id": ObjectId(trade_id)})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade offer not found")

    is_receiver = trade["receiver_id"] == user["_id"]

    counter_offers = trade.get("counter_offers", [])
    if counter_offers:
        last_counter_by = counter_offers[-1]["by_user_id"]
        if last_counter_by == user["_id"]:
            raise HTTPException(status_code=403, detail="Waiting for the other party to respond")
    elif not is_receiver:
        raise HTTPException(status_code=403, detail="Only the receiver can respond to this offer")

    if trade["status"] not in ["pending", "countered"]:
        raise HTTPException(status_code=400, detail=f"Trade is already {trade['status']}")

    if data.action not in ["accept", "decline"]:
        raise HTTPException(status_code=400, detail="Action must be 'accept' or 'decline'")

    now = datetime.now(timezone.utc).isoformat()
    new_status = "accepted" if data.action == "accept" else "declined"

    await db.trade_deals.update_one(
        {"_id": ObjectId(trade_id)},
        {"$set": {"status": new_status, "updated_at": now, "completed_at": now}}
    )

    other_id = trade["proposer_id"] if is_receiver else trade["receiver_id"]

    background_tasks.add_task(
        send_push_notification,
        user_id=other_id,
        title=f"Trade offer {new_status}",
        body=f"{user.get('name', 'Someone')} {new_status} your trade offer",
        data={"type": "trade_response", "trade_id": trade_id, "url": "/"}
    )

    await manager.send_personal_message({
        "type": "trade_response",
        "trade_id": trade_id,
        "action": new_status,
        "by_user_name": user.get("name", "Unknown")
    }, other_id)

    return {"message": f"Trade offer {new_status}", "status": new_status}


@router.post("/{trade_id}/counter")
async def counter_trade_offer(trade_id: str, data: TradeCounterOffer, request: Request, background_tasks: BackgroundTasks):
    """Submit a counter-offer on an existing trade"""
    user = await get_current_user(request)

    trade = await db.trade_deals.find_one({"_id": ObjectId(trade_id)})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade offer not found")

    if trade["status"] not in ["pending", "countered"]:
        raise HTTPException(status_code=400, detail=f"Cannot counter a {trade['status']} trade")

    is_receiver = trade["receiver_id"] == user["_id"]
    is_proposer = trade["proposer_id"] == user["_id"]

    if not is_receiver and not is_proposer:
        raise HTTPException(status_code=403, detail="Not authorized for this trade")

    counter_offers = trade.get("counter_offers", [])
    if counter_offers and counter_offers[-1]["by_user_id"] == user["_id"]:
        raise HTTPException(status_code=400, detail="Waiting for the other party to respond")
    if not counter_offers and is_proposer:
        raise HTTPException(status_code=400, detail="You cannot counter your own initial offer")

    if not data.offering or not data.requesting:
        raise HTTPException(status_code=400, detail="Both offering and requesting items are required")

    now = datetime.now(timezone.utc).isoformat()
    counter_doc = {
        "id": str(ObjectId()),
        "by_user_id": user["_id"],
        "by_user_name": user.get("name", "Unknown"),
        "offering": data.offering,
        "requesting": data.requesting,
        "message": encrypt_data(data.message) if data.message else "",
        "created_at": now
    }

    await db.trade_deals.update_one(
        {"_id": ObjectId(trade_id)},
        {
            "$push": {"counter_offers": counter_doc},
            "$set": {
                "status": "countered",
                "updated_at": now,
                "offering": data.offering if is_proposer else trade["offering"],
                "requesting": data.requesting if is_proposer else trade["requesting"]
            }
        }
    )

    other_id = trade["proposer_id"] if is_receiver else trade["receiver_id"]

    background_tasks.add_task(
        send_push_notification,
        user_id=other_id,
        title=f"Counter-offer from {user.get('name', 'Someone')}",
        body=f"Offering: {', '.join(data.offering[:2])}",
        data={"type": "trade_counter", "trade_id": trade_id, "url": "/"}
    )

    await manager.send_personal_message({
        "type": "trade_counter",
        "trade_id": trade_id,
        "by_user_name": user.get("name", "Unknown"),
        "offering": data.offering,
        "requesting": data.requesting
    }, other_id)

    return {"message": "Counter-offer submitted", "status": "countered"}


@router.post("/{trade_id}/cancel")
async def cancel_trade(trade_id: str, request: Request, background_tasks: BackgroundTasks):
    """Cancel a trade offer"""
    user = await get_current_user(request)

    trade = await db.trade_deals.find_one({"_id": ObjectId(trade_id)})
    if not trade:
        raise HTTPException(status_code=404, detail="Trade offer not found")

    if trade["proposer_id"] != user["_id"] and trade["receiver_id"] != user["_id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    if trade["status"] not in ["pending", "countered"]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {trade['status']} trade")

    now = datetime.now(timezone.utc).isoformat()
    await db.trade_deals.update_one(
        {"_id": ObjectId(trade_id)},
        {"$set": {"status": "cancelled", "updated_at": now, "completed_at": now}}
    )

    other_id = trade["receiver_id"] if trade["proposer_id"] == user["_id"] else trade["proposer_id"]

    background_tasks.add_task(
        send_push_notification,
        user_id=other_id,
        title="Trade offer cancelled",
        body=f"{user.get('name', 'Someone')} cancelled the trade offer",
        data={"type": "trade_cancelled", "trade_id": trade_id, "url": "/"}
    )

    return {"message": "Trade offer cancelled", "status": "cancelled"}
