from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual, get_admin_atual
from app.agentes.model import Agente


from app.dependencies import get_db
from app.enderecos.repository import EnderecoRepository
from app.enderecos.schema import (
    EnderecoCreate,
    EnderecoUpdate,
    EnderecoResponse
)
from app.enderecos.service import EnderecoService


router = APIRouter(
    prefix="/enderecos",
    tags=["Endereços"]
)


@router.post(
    "",
    response_model=EnderecoResponse,
    status_code=201
)
def criar_endereco(
    dados: EnderecoCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

    try:

        return service.criar(dados)

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.get(
    "",
    response_model=list[EnderecoResponse]
)
def listar_enderecos(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

    return service.listar()


@router.get(
    "/{id}",
    response_model=EnderecoResponse
)
def buscar_endereco(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

    try:

        return service.buscar_por_id(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.get(
    "/pessoa/{pessoa_id}",
    response_model=list[EnderecoResponse]
)
def listar_enderecos_por_pessoa(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

    try:

        return service.listar_por_pessoa(pessoa_id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.put(
    "/{id}",
    response_model=EnderecoResponse
)
def atualizar_endereco(
    id: UUID,
    dados: EnderecoUpdate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

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
def deletar_endereco(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = EnderecoRepository(db)

    service = EnderecoService(repository)

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )