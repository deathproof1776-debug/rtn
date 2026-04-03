"""
Routes package - modular API endpoints for Rebel Trade Network.
"""
from fastapi import APIRouter

# Import all route modules
from .auth import router as auth_router
from .profile import router as profile_router
from .posts import router as posts_router
from .messaging import router as messaging_router
from .network import router as network_router
from .trades import router as trades_router
from .gallery import router as gallery_router
from .uploads import router as uploads_router
from .admin import router as admin_router
from .notifications import router as notifications_router
from .categories import router as categories_router
from .invites import router as invites_router
from .community import router as community_router

# Create main API router
api_router = APIRouter(prefix="/api")

# Include all sub-routers
api_router.include_router(auth_router, tags=["Authentication"])
api_router.include_router(profile_router, tags=["Profile"])
api_router.include_router(posts_router, tags=["Posts"])
api_router.include_router(messaging_router, tags=["Messaging"])
api_router.include_router(network_router, tags=["Trade Network"])
api_router.include_router(trades_router, tags=["Trade Deals"])
api_router.include_router(gallery_router, tags=["Gallery"])
api_router.include_router(uploads_router, tags=["Uploads"])
api_router.include_router(admin_router, tags=["Admin"])
api_router.include_router(notifications_router, tags=["Notifications"])
api_router.include_router(categories_router, tags=["Categories"])
api_router.include_router(invites_router, tags=["Invites"])
api_router.include_router(community_router, tags=["Community"])


# Health check at API root
@api_router.get("/")
async def root():
    return {"message": "Rebel Trade Network API", "status": "running"}
