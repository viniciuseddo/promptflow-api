from fastapi import APIRouter

from app.api.routes import generations, health, templates

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(templates.router, prefix="/templates", tags=["Templates"])
api_router.include_router(
    generations.router, prefix="/generations", tags=["Generations"]
)

