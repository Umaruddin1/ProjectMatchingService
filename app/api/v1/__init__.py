"""__init__ for v1 API."""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, process, reconcile, export

router = APIRouter(prefix="/api/v1")

# Include endpoint routers
router.include_router(auth.router)
router.include_router(process.router)
router.include_router(reconcile.router)
router.include_router(export.router)
