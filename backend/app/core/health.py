from fastapi import APIRouter
from sqlalchemy import text

from app.core.db import DbSession

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness: the process is up."""
    return {"status": "ok"}


@router.get("/health/ready")
def ready(session: DbSession) -> dict[str, str]:
    """Readiness: the database is reachable."""
    session.execute(text("SELECT 1"))
    return {"status": "ok"}
