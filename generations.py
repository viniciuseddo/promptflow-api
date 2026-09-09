from typing import Annotated, Literal

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.generation import GenerationCreate, GenerationRead
from app.services.generation import GenerationService

router = APIRouter()
service = GenerationService()

GENERATION_ERRORS = {
    404: {"model": ErrorResponse, "description": "Recurso não encontrado"},
    422: {"model": ErrorResponse, "description": "Regra de negócio violada"},
    502: {"model": ErrorResponse, "description": "Erro do provedor LLM"},
    503: {"model": ErrorResponse, "description": "Provedor não configurado"},
    504: {"model": ErrorResponse, "description": "Timeout do provedor LLM"},
}


@router.post(
    "",
    response_model=GenerationRead,
    status_code=status.HTTP_201_CREATED,
    responses=GENERATION_ERRORS,
    summary="Gera conteúdo usando um template",
)
def create_generation(
    data: GenerationCreate,
    db: Annotated[Session, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> GenerationRead:
    return service.create(db, data, settings)


@router.get("", response_model=list[GenerationRead], summary="Lista o histórico")
def list_generations(
    db: Annotated[Session, Depends(get_db)],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    template_id: int | None = Query(default=None, gt=0),
    status_filter: Literal["processing", "success", "failed"] | None = Query(
        default=None, alias="status"
    ),
) -> list[GenerationRead]:
    return service.list(
        db,
        offset=offset,
        limit=limit,
        template_id=template_id,
        status=status_filter,
    )


@router.get(
    "/{generation_id}",
    response_model=GenerationRead,
    responses={404: GENERATION_ERRORS[404]},
    summary="Consulta uma geração",
)
def get_generation(
    generation_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> GenerationRead:
    return service.get(db, generation_id)


@router.delete(
    "/{generation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: GENERATION_ERRORS[404]},
    summary="Exclui um item do histórico",
)
def delete_generation(
    generation_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service.delete(db, generation_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

