from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import ErrorResponse
from app.schemas.prompt_template import (
    PromptTemplateCreate,
    PromptTemplateRead,
    PromptTemplateUpdate,
)
from app.services.prompt_template import PromptTemplateService

router = APIRouter()
service = PromptTemplateService()

ERROR_RESPONSES = {
    404: {"model": ErrorResponse, "description": "Template não encontrado"},
    409: {"model": ErrorResponse, "description": "Conflito de regra de negócio"},
    422: {"model": ErrorResponse, "description": "Dados ou template inválido"},
}


@router.post(
    "",
    response_model=PromptTemplateRead,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
    summary="Cria um template",
)
def create_template(
    data: PromptTemplateCreate,
    db: Annotated[Session, Depends(get_db)],
) -> PromptTemplateRead:
    return service.create(db, data)


@router.get("", response_model=list[PromptTemplateRead], summary="Lista templates")
def list_templates(
    db: Annotated[Session, Depends(get_db)],
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
) -> list[PromptTemplateRead]:
    return service.list(db, offset=offset, limit=limit)


@router.get(
    "/{template_id}",
    response_model=PromptTemplateRead,
    responses={404: ERROR_RESPONSES[404]},
    summary="Consulta um template",
)
def get_template(
    template_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> PromptTemplateRead:
    return service.get(db, template_id)


@router.patch(
    "/{template_id}",
    response_model=PromptTemplateRead,
    responses=ERROR_RESPONSES,
    summary="Atualiza parcialmente um template",
)
def update_template(
    template_id: int,
    data: PromptTemplateUpdate,
    db: Annotated[Session, Depends(get_db)],
) -> PromptTemplateRead:
    return service.update(db, template_id, data)


@router.delete(
    "/{template_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: ERROR_RESPONSES[404], 409: ERROR_RESPONSES[409]},
    summary="Exclui um template sem histórico",
)
def delete_template(
    template_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    service.delete(db, template_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

