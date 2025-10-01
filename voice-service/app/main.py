"""
Voice Analysis Service - FastAPI Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Voice analysis microservice with gender-aware emotion detection"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Voice Analysis Service",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers (will be added later)
# from app.api.v1.endpoints import analyze, prompts
# app.include_router(analyze.router, prefix=f"{settings.API_V1_PREFIX}/voice-analysis", tags=["voice-analysis"])
# app.include_router(prompts.router, prefix=f"{settings.API_V1_PREFIX}/voice-analysis", tags=["prompts"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
