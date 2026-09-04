"""FastAPI 入口。"""

from fastapi import FastAPI

from app.config import get_settings
from app.http.routes import router


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, debug=settings.debug)
    app.include_router(router, prefix="/api", tags=["chat"])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
