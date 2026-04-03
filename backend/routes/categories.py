"""
Categories API routes: get predefined categories for goods, skills, services.
"""
from fastapi import APIRouter

from categories import GOODS_CATEGORIES, SKILLS_CATEGORIES, SERVICES_CATEGORIES

router = APIRouter(prefix="/categories")


@router.get("/goods")
async def get_goods_categories():
    """Get all predefined goods categories with items"""
    return {"categories": GOODS_CATEGORIES}


@router.get("/skills")
async def get_skills_categories():
    """Get all predefined skills categories with items"""
    return {"categories": SKILLS_CATEGORIES}


@router.get("/services")
async def get_services_categories():
    """Get all predefined services categories with items"""
    return {"categories": SERVICES_CATEGORIES}


@router.get("/all")
async def get_all_categories():
    """Get all predefined categories for goods, skills, and services"""
    return {
        "goods": GOODS_CATEGORIES,
        "skills": SKILLS_CATEGORIES,
        "services": SERVICES_CATEGORIES
    }
