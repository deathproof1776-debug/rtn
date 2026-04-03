"""
Push notification routes: subscribe, unsubscribe, test.
"""
from fastapi import APIRouter, Request

from database import db
from auth import get_current_user
from models import PushSubscription
from notifications import send_push_notification, get_vapid_public_key
from datetime import datetime, timezone

router = APIRouter(prefix="/notifications")


@router.get("/vapid-public-key")
async def get_vapid_key():
    """Get VAPID public key for frontend push subscription"""
    return {"publicKey": get_vapid_public_key()}


@router.post("/subscribe")
async def subscribe_push(subscription: PushSubscription, request: Request):
    """Subscribe to push notifications"""
    user = await get_current_user(request)

    existing = await db.push_subscriptions.find_one({
        "user_id": user["_id"],
        "endpoint": subscription.endpoint
    })

    if existing:
        return {"message": "Already subscribed", "subscribed": True}

    sub_doc = {
        "user_id": user["_id"],
        "endpoint": subscription.endpoint,
        "keys": subscription.keys,
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    await db.push_subscriptions.insert_one(sub_doc)

    return {"message": "Subscribed to push notifications", "subscribed": True}


@router.post("/unsubscribe")
async def unsubscribe_push(subscription: PushSubscription, request: Request):
    """Unsubscribe from push notifications"""
    user = await get_current_user(request)

    result = await db.push_subscriptions.delete_one({
        "user_id": user["_id"],
        "endpoint": subscription.endpoint
    })

    if result.deleted_count > 0:
        return {"message": "Unsubscribed from push notifications", "subscribed": False}
    return {"message": "Subscription not found", "subscribed": False}


@router.get("/status")
async def get_notification_status(request: Request):
    """Get user's push notification subscription status"""
    user = await get_current_user(request)

    count = await db.push_subscriptions.count_documents({"user_id": user["_id"]})
    return {"subscribed": count > 0, "subscription_count": count}


@router.post("/test")
async def test_push_notification(request: Request):
    """Send a test push notification to the current user"""
    user = await get_current_user(request)

    await send_push_notification(
        user_id=user["_id"],
        title="Rebel Trade Network Test",
        body="Push notifications are working! You'll receive alerts for messages, comments, and matches.",
        data={"type": "test", "url": "/"}
    )

    return {"message": "Test notification sent"}
