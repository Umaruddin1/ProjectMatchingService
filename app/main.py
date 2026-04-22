"""Main FastAPI application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging_config import logger
from app.api.v1 import router as v1_router

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.API_VERSION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(v1_router)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": settings.PROJECT_NAME}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.API_VERSION,
        "endpoints": {
            "process": "POST /api/v1/process - Upload and process Excel workbook",
            "reconcile": "POST /api/v1/reconcile - Reconcile and finalize matches",
            "export": "POST /api/v1/export - Generate Excel export",
        }
    }

if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {settings.PROJECT_NAME}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
