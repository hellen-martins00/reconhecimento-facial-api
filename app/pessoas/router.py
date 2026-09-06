from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual, get_admin_atual
from app.agentes.model import Agente

from app.dependencies import get_db
from app.pessoas.repository import PessoaRepository
from app.pessoas.schema import (
    PessoaCreate,
    PessoaUpdate,
    PessoaResponse,
    PessoaListaResponse
)
from app.pessoas.service import PessoaService


router = APIRouter(
    prefix="/pessoas",
    tags=["Pessoas"]
)


# CRIAR PESSOA

@router.post(
    "",
    response_model=PessoaResponse,
    status_code=201
)
def criar_pessoa(
    dados: PessoaCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PessoaRepository(db)

    service = PessoaService(repository)

    try:

        pessoa = service.criar(dados)

        return pessoa

    except ValueError as erro:

        raise HTTPException(
            status_code=409,
            detail=str(erro)
        )


# LISTAR PESSOAS

@router.get(
    "",
    response_model=list[PessoaListaResponse]
)
def listar_pessoas(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PessoaRepository(db)

    service = PessoaService(repository)

    return service.listar()


# BUSCAR PESSOA

@router.get(
    "/{id}",
    response_model=PessoaResponse
)
def buscar_pessoa(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PessoaRepository(db)

    service = PessoaService(repository)

    pessoa = service.buscar_por_id(id)

    if not pessoa:

        raise HTTPException(
            status_code=404,
            detail="Pessoa não encontrada."
        )

    return pessoa


# ATUALIZAR PESSOA

@router.put(
    "/{id}",
    response_model=PessoaResponse
)
def atualizar_pessoa(
    id: UUID,
    dados: PessoaUpdate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PessoaRepository(db)

    service = PessoaService(repository)

    try:

        return service.atualizar(id, dados)

    except ValueError as erro:

        mensagem = str(erro)

        if mensagem == "Pessoa não encontrada.":

            raise HTTPException(
                status_code=404,
                detail=mensagem
            )

        raise HTTPException(
            status_code=409,
            detail=mensagem
        )


# DELETAR PESSOA

@router.delete(
    "/{id}",
    status_code=204
)
def deletar_pessoa(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = PessoaRepository(db)

    service = PessoaService(repository)

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )