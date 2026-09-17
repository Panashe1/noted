from fastapi import APIRouter
from sqlalchemy import text

from app.core.deps import DbSession
from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(db: DbSession) -> HealthResponse:
    try:
        await db.execute(text("SELECT 1"))
        database = "ok"
    except Exception:  # noqa: BLE001 - any failure means the DB is unavailable
        database = "unavailable"
    return HealthResponse(status="ok", version="0.1.0", database=database)
