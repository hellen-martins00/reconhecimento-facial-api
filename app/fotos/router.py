from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from fastapi.responses import Response

from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual, get_admin_atual
from app.agentes.model import Agente

from app.dependencies import get_db

from app.fotos.repository import FotoRepository
from app.fotos.schema import FotoResponse
from app.fotos.service import FotoService

from app.embeddings.service import EmbeddingService
from app.embeddings.repository import EmbeddingRepository


router = APIRouter(
    prefix="/fotos",
    tags=["Fotos"]
)


@router.post(
    "",
    response_model=FotoResponse,
    status_code=201
)
def criar_foto(
    pessoa_id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    foto_repository = FotoRepository(db)

    embedding_service = EmbeddingService()

    embedding_repository = EmbeddingRepository(db)

    service = FotoService(
        repository=foto_repository,
        embedding_service=embedding_service,
        embedding_repository=embedding_repository
    )

    try:

        return service.criar(
            pessoa_id,
            arquivo
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


@router.get(
    "",
    response_model=list[FotoResponse]
)
def listar_fotos(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    service = FotoService(
        repository=repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db)
    )

    return service.listar()

@router.get(
    "/{id}/arquivo"
)
def carregar_foto(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    foto = repository.buscar_por_id(id)

    if not foto:

        raise HTTPException(
            status_code=404,
            detail="Foto não encontrada."
        )

    nome = foto.nome_arquivo.lower()

    if nome.endswith(".jpg") or nome.endswith(".jpeg"):

        media_type = "image/jpeg"

    elif nome.endswith(".png"):

        media_type = "image/png"

    else:

        media_type = "application/octet-stream"

    return Response(
        content=foto.arquivo,
        media_type=media_type
    )

@router.get(
    "/{id}",
    response_model=FotoResponse
)
def buscar_foto(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    service = FotoService(
        repository=repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db)
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
    response_model=list[FotoResponse]
)
def listar_fotos_por_pessoa(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    service = FotoService(
        repository=repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db)
    )

    return service.listar_por_pessoa(pessoa_id)


@router.delete(
    "/{id}",
    status_code=204
)
def deletar_foto(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = FotoRepository(db)

    service = FotoService(
        repository=repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db)
    )

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )
        
@router.put(
    "/{id}",
    response_model=FotoResponse
)
def atualizar_foto(
    id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    foto_repository = FotoRepository(db)

    embedding_service = EmbeddingService()

    embedding_repository = EmbeddingRepository(db)

    service = FotoService(
        repository=foto_repository,
        embedding_service=embedding_service,
        embedding_repository=embedding_repository
    )

    try:

        return service.atualizar_foto_pessoa(
            id,
            arquivo
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )
        
@router.get(
    "/pessoa/{pessoa_id}/mais-recente/arquivo"
)
def carregar_foto_mais_recente(
    pessoa_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    foto = repository.buscar_mais_recente_por_pessoa(
        pessoa_id
    )

    if not foto:
        raise HTTPException(
            status_code=404,
            detail="Pessoa não possui foto."
        )

    nome = foto.nome_arquivo.lower()

    if nome.endswith(".jpg") or nome.endswith(".jpeg"):
        media_type = "image/jpeg"

    elif nome.endswith(".png"):
        media_type = "image/png"

    else:
        media_type = "application/octet-stream"

    return Response(
        content=foto.arquivo,
        media_type=media_type
    )