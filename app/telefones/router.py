from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual, get_admin_atual
from app.agentes.model import Agente

from app.dependencies import get_db
from app.telefones.repository import TelefoneRepository
from app.telefones.schema import (
    TelefoneCreate,
    TelefoneUpdate,
    TelefoneResponse
)
from app.telefones.service import TelefoneService


router = APIRouter(
    prefix="/telefones",
    tags=["Telefones"]
)


@router.post(
    "",
    response_model=TelefoneResponse,
    status_code=201
)
def criar_telefone(
    dados: TelefoneCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    try:

        return service.criar(dados)

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.get(
    "",
    response_model=list[TelefoneResponse]
)
def listar_telefones(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):
    
    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    return service.listar()


@router.get(
    "/{id}",
    response_model=TelefoneResponse
)
def buscar_telefone(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    try:

        return service.buscar_por_id(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.get(
    "/pessoa/{pessoa_id}",
    response_model=list[TelefoneResponse]
)
def listar_telefones_por_pessoa(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    try:

        return service.listar_por_pessoa(pessoa_id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.put(
    "/{id}",
    response_model=TelefoneResponse
)
def atualizar_telefone(
    id: UUID,
    dados: TelefoneUpdate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    try:

        return service.atualizar(id, dados)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.delete(
    "/{id}",
    status_code=204
)
def deletar_telefone(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = TelefoneRepository(db)

    service = TelefoneService(repository)

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )