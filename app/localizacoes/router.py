
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.auth.dependencies import get_agente_atual
from app.agentes.model import Agente

from app.desaparecimentos.repository import (
    RegistroDesaparecimentoRepository,
)
from app.localizacoes.repository import (
    LocalizacaoPessoaRepository,
)
from app.localizacoes.schema import (
    LocalizacaoPessoaCreate,
    LocalizacaoPessoaResponse,
)
from app.localizacoes.service import LocalizacaoPessoaService


router = APIRouter(
    prefix="/localizacoes",
    tags=["Localizações"],
)


def obter_service(db: Session) -> LocalizacaoPessoaService:
    localizacao_repository = LocalizacaoPessoaRepository(db)
    desaparecimento_repository = RegistroDesaparecimentoRepository(db)

    return LocalizacaoPessoaService(
        repository=localizacao_repository,
        desaparecimento_repository=desaparecimento_repository,
    )


@router.post(
    "",
    response_model=LocalizacaoPessoaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_localizacao(
    dados: LocalizacaoPessoaCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.criar(
            registro_desaparecimento_id=dados.registro_desaparecimento_id,
            local_informado=dados.local_informado,
            data_hora=dados.data_hora,
            descricao=dados.descricao,
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro


@router.get(
    "",
    response_model=list[LocalizacaoPessoaResponse],
)
def listar_localizacoes(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)
    return service.listar()


@router.get(
    "/registro/{registro_desaparecimento_id}",
    response_model=list[LocalizacaoPessoaResponse],
)
def listar_localizacoes_por_registro(
    registro_desaparecimento_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.listar_por_registro(
            registro_desaparecimento_id
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        ) from erro
