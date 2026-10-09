from fastapi import FastAPI, status
from app import models
from app.database import Base, engine
from app.routers import auth, tasks

# Create database tables for all imported models on startup
Base.metadata.create_all(bind=engine)

# Create FastAPI application instance
app = FastAPI(title="Task Manager API")

# Include API routers
app.include_router(auth.router)
app.include_router(tasks.router)


@app.get("/", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Public health check endpoint returning operational status."""
    return {"status": "ok"}
