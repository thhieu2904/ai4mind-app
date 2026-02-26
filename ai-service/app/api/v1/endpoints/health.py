"""
Health check endpoint
"""

from fastapi import APIRouter

router = APIRouter()


@router.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint - supports GET and HEAD (for UptimeRobot)"""
    return {
        "status": "healthy",
        "service": "ai-service"
    }


@router.api_route("/ping", methods=["GET", "HEAD"])
async def ping():
    """Ping endpoint"""
    return {"message": "pong"}
