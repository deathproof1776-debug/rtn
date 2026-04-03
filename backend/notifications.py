"""
Push notification helpers using Web Push (VAPID).
"""
import os
import json
import logging
from datetime import datetime, timezone
from pywebpush import webpush, WebPushException

from database import db

logger = logging.getLogger(__name__)

# VAPID Configuration
VAPID_PUBLIC_KEY = os.environ.get("VAPID_PUBLIC_KEY", "")
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_CLAIMS_EMAIL = os.environ.get("VAPID_CLAIMS_EMAIL", "admin@homesteadhub.com")


async def send_push_notification(
    user_id: str,
    title: str,
    body: str,
    data: dict = None,
    icon: str = "/logo192.png"
):
    """Send push notification to all subscribed devices of a user"""
    if not VAPID_PUBLIC_KEY or not VAPID_PRIVATE_KEY:
        logger.warning("VAPID keys not configured, skipping push notification")
        return

    subscriptions = await db.push_subscriptions.find({"user_id": user_id}).to_list(100)

    notification_payload = json.dumps({
        "title": title,
        "body": body,
        "icon": icon,
        "data": data or {},
        "timestamp": datetime.now(timezone.utc).isoformat()
    })

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub["endpoint"],
                    "keys": {
                        "p256dh": sub["keys"]["p256dh"],
                        "auth": sub["keys"]["auth"]
                    }
                },
                data=notification_payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": f"mailto:{VAPID_CLAIMS_EMAIL}"}
            )
            logger.info(f"Push notification sent to user {user_id}")
        except WebPushException as e:
            logger.error(f"Push notification failed: {e}")
            # Remove invalid subscription (410 Gone or 404 Not Found)
            if e.response and e.response.status_code in [404, 410]:
                await db.push_subscriptions.delete_one({"_id": sub["_id"]})
                logger.info(f"Removed invalid subscription for user {user_id}")


def get_vapid_public_key() -> str:
    """Get the VAPID public key for frontend subscription."""
    return VAPID_PUBLIC_KEY
