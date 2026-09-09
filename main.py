from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.handlers import register_exception_handlers
from app.db.init_db import init_db


def create_app(*, initialize_database: bool = True) -> FastAPI:
    settings = get_settings()

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        if initialize_database:
            init_db()
        yield

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "API REST para gerenciar templates de prompt e consumir provedores LLM "
            "com histórico persistente."
        ),
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )
    application.include_router(api_router, prefix="/api/v1")
    register_exception_handlers(application)
    return application


app = create_app()

