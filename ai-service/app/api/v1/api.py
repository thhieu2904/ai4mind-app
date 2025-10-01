"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, assessments

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])

# Add more routers here as we implement them
# api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
# api_router.include_router(consents.router, prefix="/consents", tags=["Parent Consents"])
