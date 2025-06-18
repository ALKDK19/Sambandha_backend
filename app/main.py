from datetime import datetime

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth, users, profiles, preferences,
    likes, matches, chats, messages,
    notifications, admin
)
from app.config import settings
from app.database import engine
from app.models.base import Base

app = FastAPI(
    title="Sambandha API",
    version="1.0.0",
    description="Backend API for Sambandha - Nepali Matrimonial App",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS + settings.ADMIN_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables (for development)
Base.metadata.create_all(bind=engine)

# Include API routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(profiles.router, prefix="/api/profiles", tags=["Profiles"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["Preferences"])
app.include_router(likes.router, prefix="/api/likes", tags=["Likes & Matches"])
app.include_router(matches.router, prefix="/api/matches", tags=["Likes & Matches"])
app.include_router(chats.router, prefix="/api/chats", tags=["Messaging"])
app.include_router(messages.router, prefix="/api/messages", tags=["Messaging"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])


# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Sambandha API",
        "docs": "/api/docs",
        "redoc": "/api/redoc"
    }
