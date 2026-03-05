"""
FastAPI Application Entry Point
AI4Mind API Gateway
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.api.v1.api import api_router

# Initialize FastAPI app
app = FastAPI(
    title="AI4Mind API Gateway",
    description="Backend API Gateway for AI4Mind Mental Health Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,  # Use property to parse from string
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    errors = exc.errors()
    # Convert errors to JSON-serializable format
    formatted_errors = []
    for error in errors:
        error_dict = dict(error)
        # Convert ctx values to strings if they're not JSON serializable
        if 'ctx' in error_dict and 'error' in error_dict['ctx']:
            error_dict['ctx']['error'] = str(error_dict['ctx']['error'])
        # Convert bytes input to string for JSON serialization
        if 'input' in error_dict and isinstance(error_dict['input'], bytes):
            error_dict['input'] = error_dict['input'].decode('utf-8', errors='replace')
        formatted_errors.append(error_dict)
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": formatted_errors,
            "message": "Validation error"
        }
    )


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "Database error occurred",
            "detail": str(exc) if settings.ENVIRONMENT == "development" else "Internal server error"
        }
    )


@app.get("/")
async def root():
    """Root endpoint - Health check"""
    return {
        "message": "AI4Mind API Gateway",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


@app.api_route("/health", methods=["GET", "HEAD"])
async def health_check():
    """Health check endpoint - supports GET and HEAD (for UptimeRobot)"""
    return {
        "status": "healthy",
        "service": "ai-service",
        "environment": settings.ENVIRONMENT
    }


# Include API v1 router
app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
