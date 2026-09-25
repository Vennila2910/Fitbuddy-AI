from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .database import init_db
from .routes import router


# Project root directory
BASE_DIR = Path(__file__).resolve().parent.parent


# Create FastAPI application
app = FastAPI(
    title="FitBuddy - AI Fitness Plan Generator",
    description="AI-powered personalized 7-day fitness planning application.",
    version="1.0.0",
)


# Serve CSS, JavaScript, images, etc.
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static",
)


# Register application routes
app.include_router(router)


# Initialize database when the application starts
@app.on_event("startup")
def startup():
    init_db()