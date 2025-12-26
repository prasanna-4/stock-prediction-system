"""
Stock Prediction System - Main Application
FastAPI backend for stock predictions
"""
from backend.api import market
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from backend.config.settings import settings
from backend.database.config import init_db
from backend.api import predictions, stocks, performance, health

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup and shutdown events
    """
    # Startup
    logger.info(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("📊 Initializing database...")
    init_db()
    logger.info("✅ Database initialized")
    
    # TODO: Initialize Redis connection
    # TODO: Load ML models
    # TODO: Start background tasks for data fetching
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down application...")
    # TODO: Cleanup tasks


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Stock Prediction System with ML",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# API Key authentication dependency
async def verify_api_key(x_api_key: str = Header(...)):
    """
    Verify API key from request header
    """
    if x_api_key != settings.API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key


# Include routers
app.include_router(
    health.router,
    prefix="/api/v1",
    tags=["Health"]
)

app.include_router(
    stocks.router,
    prefix="/api/v1/stocks",
    tags=["Stocks"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    predictions.router,
    prefix="/api/v1/predictions",
    tags=["Predictions"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    performance.router,
    prefix="/api/v1/performance",
    tags=["Performance"],
    dependencies=[Depends(verify_api_key)]
)

app.include_router(
    market.router,
    prefix="/api/v1/market",
    tags=["Market Data"],
    dependencies=[Depends(verify_api_key)]
)


@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/api/docs"
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
