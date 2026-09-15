from fastapi import FastAPI

from backend.api.routes import router
from backend.models.database import Base, engine
from backend.models.receipt import Receipt


app = FastAPI(
    title="Receipt Extractor API",
    description="AI-powered receipt extraction service",
    version="1.0.0",
)


# Create database tables
Base.metadata.create_all(bind=engine)

# Register API routes
app.include_router(router)


@app.get("/")
def root():
    return {
        "message": "Receipt Extractor API is running",
        "status": "healthy",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}