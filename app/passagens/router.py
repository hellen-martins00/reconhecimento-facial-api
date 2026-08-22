from datetime import date
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual, get_admin_atual
from app.agentes.model import Agente

from app.dependencies import get_db

from app.passagens.repository import PassagemRepository
from app.passagens.schema import PassagemCriminalResponse
from app.passagens.service import PassagemService


router = APIRouter(
    prefix="/passagens",
    tags=["Passagens Criminais"]
)


@router.post(
    "",
    response_model=PassagemCriminalResponse,
    status_code=201
)
def criar_passagem(
    pessoa_id: UUID,
    crime: str,
    descricao: str,
    data_ocorrencia: date,
    delegacia: str,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PassagemRepository(db)

    service = PassagemService(
        repository
    )

    try:

        return service.criar(
            pessoa_id=pessoa_id,
            crime=crime,
            descricao=descricao,
            data_ocorrencia=data_ocorrencia,
            delegacia=delegacia
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.get(
    "",
    response_model=list[PassagemCriminalResponse]
)
def listar_passagens(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PassagemRepository(db)

    service = PassagemService(
        repository
    )

    return service.listar()


@router.get(
    "/{id}",
    response_model=PassagemCriminalResponse
)
def buscar_passagem(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PassagemRepository(db)

    service = PassagemService(
        repository
    )

    try:

        return service.buscar_por_id(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


@router.get(
    "/pessoa/{pessoa_id}",
    response_model=list[PassagemCriminalResponse]
)
def listar_passagens_por_pessoa(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = PassagemRepository(db)

    service = PassagemService(
        repository
    )

    return service.listar_por_pessoa(
        pessoa_id
    )


@router.delete(
    "/{id}",
    status_code=204
)
def deletar_passagem(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = PassagemRepository(db)

    service = PassagemService(
        repository
    )

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )