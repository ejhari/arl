"""ARL FastAPI Application"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api.router import api_router
from app.core.redis import pubsub, close_redis_client
from app.core.websocket import socket_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events"""
    # Startup
    print("🚀 Starting ARL Backend...")
    print("📡 Initializing Redis PubSub...")
    await pubsub.initialize()
    print("✅ Redis PubSub initialized")
    yield
    # Shutdown
    print("👋 Shutting down ARL Backend...")
    print("🔌 Closing Redis connections...")
    await pubsub.close()
    await close_redis_client()
    print("✅ Redis connections closed")


app = FastAPI(
    title="ARL API",
    description="Autonomous Research Lab API",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount Socket.IO app
app.mount("/ws", socket_app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "websocket": "enabled"
    }
