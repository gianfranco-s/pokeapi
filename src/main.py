from fastapi import FastAPI

from src.cache import create_cache
from src.dependencies import get_settings
from src.router import router


def create_app() -> FastAPI:
    app = FastAPI(title="Poke-berries Statistics API")

    settings = get_settings()
    app.state.cache = create_cache(settings.redis_url)

    app.include_router(router)
    return app


app = create_app()
