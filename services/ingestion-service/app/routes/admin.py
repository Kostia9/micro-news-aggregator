from fastapi import APIRouter

from app.schemas.source import SourceConfig
from app.sources import RSS_SOURCES

router = APIRouter(prefix="/admin/sources", tags=["admin"])


@router.get("", response_model=list[SourceConfig])
async def list_sources() -> list[SourceConfig]:
    return [SourceConfig.model_validate(source) for source in RSS_SOURCES]
