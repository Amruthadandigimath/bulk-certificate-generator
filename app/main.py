from fastapi import FastAPI

from .database import Base, engine
from .routes.jobs import router as jobs_router


# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI application
app = FastAPI(
    title="Bulk Certificate Generator API",
    description="API for generating certificates in bulk.",
    version="1.0.0"
)

# Register routes
app.include_router(
    jobs_router,
    prefix="/api"
)


@app.get("/")
def root():
    return {
        "message": "Bulk Certificate Generator API is running"
    }