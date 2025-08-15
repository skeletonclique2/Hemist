from fastapi import FastAPI, HTTPException, Response, Request, Depends, status, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import structlog
import os
from contextlib import asynccontextmanager

from app.core.security import authenticate_user, create_access_token
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import langsmith
from app.database.connection import init_db
from app.api.routes import router as api_router
# Removed import of create_streamlit_app as it does not exist
# from app.frontend.streamlit_app import create_streamlit_app

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting AI Agents application")
    try:
        # Initialize LangSmith tracing
        langsmith.init(project_name="AI Agents System", tags=["production", "content-generation"])
        logger.info("LangSmith tracing initialized")
    except Exception as e:
        logger.error("Failed to initialize LangSmith tracing", error=str(e))
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Failed to initialize database", error=str(e))
        raise

    yield

    # Shutdown
    logger.info("Shutting down AI Agents application")

# Create FastAPI app
app = FastAPI(
    title="AI Agents System",
    description="Production-ready multi-agent AI system for content generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add global exception handler for high-end error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    High-end global exception handler to catch all unhandled exceptions
    and return a structured JSON response.
    """
    logger.error("Unhandled exception", exc_info=exc, request_url=str(request.url))
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "details": str(exc),
        },
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Pydantic model for login request
class LoginRequest(BaseModel):
    username: str
    password: str

# Authentication router
auth_router = APIRouter()

@auth_router.post("/login")
async def login(login_request: LoginRequest):
    """
    Authenticate a user and return a JWT access token.
    
    Args:
        login_request (LoginRequest): The login credentials.
        
    Returns:
        dict: A dictionary containing the access token and token type.
        
    Raises:
        HTTPException: If the credentials are invalid.
    """
    user = authenticate_user(login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"], "role": user["role"]})
    return {"access_token": access_token, "token_type": "bearer"}

app.include_router(auth_router, prefix="/auth")

# Health check endpoint (unprotected for monitoring)
@app.get("/health")
async def health_check():
    """Health check endpoint for Docker health checks"""
    return {
        "status": "healthy",
        "service": "ai-agents",
        "version": "1.0.0",
        "database": "connected"  # You can add actual DB health check here
    }

# Prometheus metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with system information"""
    return {
        "message": "AI Agents System",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "api": "/api/v1",
            "health": "/health",
            "frontend": "/frontend"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
