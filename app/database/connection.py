from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import structlog
import os
from typing import AsyncGenerator

logger = structlog.get_logger()

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ai_user:ai_password@localhost:5432/ai_agents")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Create base class for models
Base = declarative_base()

# Database engine configuration
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False  # Set to True for SQL debugging
)

# Async engine for async operations
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=False
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Async session factory
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("Database session error", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()

def get_sync_db():
    """Get synchronous database session"""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error("Database session error", error=str(e))
        db.rollback()
        raise
    finally:
        db.close()

async def init_db():
    """Initialize database and create tables"""
    try:
        # Test connection
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            logger.info("Database connection successful")
        
        # Create tables
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")
            
        # Verify pgvector extension
        async with async_engine.begin() as conn:
            result = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
            if result.fetchone():
                logger.info("pgvector extension is active")
            else:
                logger.warning("pgvector extension not found - vector operations may not work")
                
    except Exception as e:
        logger.warning("Database initialization failed - running in demo mode", error=str(e))
        logger.info("System will run without database functionality")
        # Don't raise the error, just log it

async def check_db_health():
    """Check database health status"""
    try:
        async with async_engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error("Database health check failed", error=str(e))
        return False

# Database models will be imported here
from app.database.models import *  # noqa 