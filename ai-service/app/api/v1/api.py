"""
API v1 router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, assessments, voice_analysis, students, combined_assessment

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(students.router, prefix="/students", tags=["Students"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(combined_assessment.router, prefix="/assessments", tags=["Combined Assessment"])  # New!
api_router.include_router(voice_analysis.router, prefix="/voice-analysis", tags=["Voice Analysis"])

# Add more routers here as we implement them
# api_router.include_router(conversations.router, prefix="/conversations", tags=["Conversations"])
# api_router.include_router(consents.router, prefix="/consents", tags=["Parent Consents"])
