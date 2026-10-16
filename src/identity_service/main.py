from fastapi import FastAPI

from identity_service.presentation.api.health import router as health_router
from identity_service.shared.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    openapi_url="/openapi.json" if settings.environment == "local" else None,
    docs_url="/docs" if settings.environment == "local" else None,
    redoc_url=None,
)
app.include_router(health_router)
