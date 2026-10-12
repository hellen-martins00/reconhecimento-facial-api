
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from app.agentes.model import Agente
from app.auth.dependencies import get_agente_atual
from app.dependencies import get_db
from app.desaparecimentos.model import RegistroDesaparecimento
from app.desaparecimentos.repository import (
    RegistroDesaparecimentoRepository,
)
from app.desaparecimentos.schema import (
    RegistroDesaparecimentoCreate,
    RegistroDesaparecimentoResponse,
    RegistroDesaparecimentoUpdate,
)
from app.desaparecimentos.service import (
    RegistroDesaparecimentoService,
)


router = APIRouter(
    prefix="/desaparecimentos",
    tags=["Registros de Desaparecimento"],
)


def obter_service(db: Session):
    repository = RegistroDesaparecimentoRepository(db)
    return RegistroDesaparecimentoService(repository)


@router.post(
    "",
    response_model=RegistroDesaparecimentoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_registro(
    dados: RegistroDesaparecimentoCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.criar(
            pessoa_id=dados.pessoa_id,
            data_desaparecimento=dados.data_desaparecimento,
            local_desaparecimento=dados.local_desaparecimento,
            descricao=dados.descricao,
            status=dados.status,
        )
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        )


@router.get(
    "",
    response_model=list[RegistroDesaparecimentoResponse],
)
def listar_registros(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    return obter_service(db).listar()


@router.get("/estatisticas")
def obter_estatisticas(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    estatisticas = db.query(
        func.count(
            case(
                (
                    RegistroDesaparecimento.status == "DESAPARECIDO",
                    1,
                )
            )
        ).label("casos_em_aberto"),
        func.count(
            case(
                (
                    RegistroDesaparecimento.status == "LOCALIZADO",
                    1,
                )
            )
        ).label("pessoas_localizadas"),
    ).one()

    return {
        "casos_em_aberto": estatisticas.casos_em_aberto,
        "pessoas_localizadas": estatisticas.pessoas_localizadas,
    }


@router.get(
    "/pessoa/{pessoa_id}",
    response_model=list[RegistroDesaparecimentoResponse],
)
def listar_por_pessoa(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.listar_por_pessoa(pessoa_id)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        )


@router.get(
    "/{id}",
    response_model=RegistroDesaparecimentoResponse,
)
def buscar_registro(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.buscar_por_id(id)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        )


@router.put(
    "/{id}",
    response_model=RegistroDesaparecimentoResponse,
)
def atualizar_registro(
    id: UUID,
    dados: RegistroDesaparecimentoUpdate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        return service.atualizar(id=id, dados=dados)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        )


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def deletar_registro(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual),
):
    service = obter_service(db)

    try:
        service.deletar(id)
    except ValueError as erro:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(erro),
        )
