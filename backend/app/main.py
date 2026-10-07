from fastapi import FastAPI

from app.core.config import get_settings
from app.core.health import router as health_router
from app.learning.router import router as learning_router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="SudoLearn API",
        version="0.1.0",
        # Interactive docs only outside production.
        docs_url="/api/docs" if settings.env != "production" else None,
        openapi_url="/api/openapi.json" if settings.env != "production" else None,
    )
    app.include_router(health_router, prefix="/api")
    app.include_router(learning_router, prefix="/api")
    return app


app = create_app()
