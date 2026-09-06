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

from app.auth.dependencies import get_agente_atual
from app.agentes.model import Agente
from app.agentes_faciais.repository import AgenteFacialRepository

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


# ============================================================
# CRIAR FOTO DE UMA PESSOA
# ============================================================

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


# ============================================================
# LISTAR TODAS AS FOTOS
# ============================================================

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


# ============================================================
# CARREGAR ARQUIVO DE UMA FOTO
# ============================================================

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


# ============================================================
# BUSCAR FOTO POR ID
# ============================================================

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


# ============================================================
# LISTAR FOTOS DE UMA PESSOA
# ============================================================

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


# ============================================================
# EXCLUIR FOTO DE UMA PESSOA
# ============================================================

@router.delete(
    "/{id}",
    status_code=204
)
def deletar_foto(
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

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )


# ============================================================
# ATUALIZAR FOTO DE UMA PESSOA
# ============================================================

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


# ============================================================
# CARREGAR FOTO MAIS RECENTE DE UMA PESSOA
# ============================================================

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


# ============================================================
# CRIAR FOTO FACIAL DE UM AGENTE
#
# AGENTE:
#   - Pode cadastrar a própria foto.
#
# ADMIN:
#   - Pode cadastrar a foto de qualquer agente.
# ============================================================

@router.post(
    "/agente/{agente_id}",
    response_model=FotoResponse,
    status_code=201
)
def criar_foto_agente(
    agente_id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    # Agente comum só pode cadastrar a própria foto.
    if (
        agente_atual.perfil != "ADMIN"
        and agente_atual.id != agente_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Você não possui permissão para cadastrar a foto deste agente."
        )

    foto_repository = FotoRepository(db)

    agente_facial_repository = AgenteFacialRepository(db)

    service = FotoService(
        repository=foto_repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db),
        agente_facial_repository=agente_facial_repository
    )

    try:

        return service.criar_para_agente(
            agente_id,
            arquivo
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


# ============================================================
# ATUALIZAR FOTO FACIAL DE UM AGENTE
#
# AGENTE:
#   - Pode atualizar a própria foto.
#
# ADMIN:
#   - Pode atualizar a foto de qualquer agente.
# ============================================================

@router.put(
    "/agente/{agente_id}",
    response_model=FotoResponse
)
def atualizar_foto_agente(
    agente_id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    # Agente comum só pode atualizar a própria foto.
    if (
        agente_atual.perfil != "ADMIN"
        and agente_atual.id != agente_id
    ):

        raise HTTPException(
            status_code=403,
            detail="Você não possui permissão para atualizar a foto deste agente."
        )

    foto_repository = FotoRepository(db)

    agente_facial_repository = AgenteFacialRepository(db)

    service = FotoService(
        repository=foto_repository,
        embedding_service=EmbeddingService(),
        embedding_repository=EmbeddingRepository(db),
        agente_facial_repository=agente_facial_repository
    )

    try:

        return service.atualizar_foto_agente(
            agente_id,
            arquivo
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )