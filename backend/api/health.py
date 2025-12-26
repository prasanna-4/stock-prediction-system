"""
Health Check API Router
Simple endpoints to check if the API is running
"""

from fastapi import APIRouter
from datetime import datetime
from backend.config.settings import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@router.get("/ping")
async def ping():
    """
    Simple ping endpoint
    """
    return {"ping": "pong"}
