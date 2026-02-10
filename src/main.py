from fastapi import FastAPI

from src.router import router


def create_app() -> FastAPI:
    app = FastAPI(title="Poke-berries Statistics API")
    app.include_router(router)
    return app

app = create_app()
