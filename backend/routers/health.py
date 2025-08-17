from fastapi import APIRouter
from datetime import datetime

from ..core.database import check_database_health

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic service health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/health/database")
async def database_health():
    """Check database connection and encryption status."""
    return check_database_health()
