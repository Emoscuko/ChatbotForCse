# backend/main.py

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.api.routes import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI.
    Handles startup and shutdown events.
    """
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="AI-powered assistant for Akdeniz University students",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(chat.router, prefix="/api/v1", tags=["chat"])


@app.get("/")
async def root():
    """
    Root endpoint - health check.
    """
    return JSONResponse(
        status_code=200,
        content={
            "message": "Welcome to the Akdeniz University AI Assistant API",
            "project": settings.PROJECT_NAME,
            "version": "1.0.0",
            "status": "running"
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    """
    return JSONResponse(
        status_code=200,
        content={"status": "healthy"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
