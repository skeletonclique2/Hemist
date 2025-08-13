from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog
import os
from contextlib import asynccontextmanager

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import langsmith
from app.database.connection import init_db
from app.api.routes import router as api_router
from app.frontend.streamlit_app import create_streamlit_app

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

# Health check endpoint
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
