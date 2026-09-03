from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    File,
    UploadFile, 
    Response,
)

from sqlalchemy.orm import Session

from app.auth.dependencies import (
    get_agente_atual,
    get_admin_atual
)

from app.agentes.model import Agente
from app.dependencies import get_db

from app.agentes.repository import AgenteRepository
from app.agentes.schema import (
    AgenteCreate,
    AgenteUpdate,
    AgenteResponse
)
from app.agentes.service import AgenteService

from app.fotos.repository import FotoRepository
from app.fotos.schema import FotoResponse
from app.fotos.service import FotoService

from app.embeddings.service import EmbeddingService
from app.embeddings.repository import EmbeddingRepository

from app.agentes_faciais.repository import AgenteFacialRepository


router = APIRouter(
    prefix="/agentes",
    tags=["Agentes"]
)


# CRIAR AGENTE
@router.post(
    "",
    response_model=AgenteResponse,
    status_code=201
)
def criar_agente(
    dados: AgenteCreate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = AgenteRepository(db)

    service = AgenteService(repository)

    try:

        return service.criar(dados)

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


# LISTAR AGENTES
@router.get(
    "",
    response_model=list[AgenteResponse]
)
def listar_agentes(
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = AgenteRepository(db)

    service = AgenteService(repository)

    return service.listar()


# BUSCAR AGENTE POR ID
@router.get(
    "/{id}",
    response_model=AgenteResponse
)
def buscar_agente(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = AgenteRepository(db)

    service = AgenteService(repository)

    agente = service.buscar_por_id(id)

    if not agente:

        raise HTTPException(
            status_code=404,
            detail="Agente não encontrado."
        )

    return agente


# ATUALIZAR AGENTE
@router.put(
    "/{id}",
    response_model=AgenteResponse
)
def atualizar_agente(
    id: UUID,
    dados: AgenteUpdate,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    # AGENTE só pode editar os próprios dados.
    # ADMIN pode editar qualquer agente.

    if (
        agente_atual.perfil != "ADMIN"
        and agente_atual.id != id
    ):
        raise HTTPException(
            status_code=403,
            detail="Você só pode editar seus próprios dados."
        )

    repository = AgenteRepository(db)

    service = AgenteService(repository)

    try:

        return service.atualizar(
            id,
            dados
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )


# CADASTRAR FOTO FACIAL DO AGENTE
@router.post(
    "/{agente_id}/foto",
    response_model=FotoResponse,
    status_code=201
)
def cadastrar_foto_facial(
    agente_id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    # ======================================================
    # PERMISSÃO
    #
    # ADMIN pode cadastrar foto de qualquer agente.
    #
    # AGENTE pode cadastrar somente a própria foto.
    # ======================================================

    if (
        agente_atual.perfil != "ADMIN"
        and agente_atual.id != agente_id
    ):
        raise HTTPException(
            status_code=403,
            detail=(
                "Você só pode cadastrar "
                "sua própria foto facial."
            )
        )

    # REPOSITÓRIOS
    foto_repository = FotoRepository(db)

    embedding_repository = EmbeddingRepository(db)

    agente_facial_repository = AgenteFacialRepository(db)

    # SERVICES

    service = FotoService(
        repository=foto_repository,
        embedding_service=EmbeddingService(),
        embedding_repository=embedding_repository,
        agente_facial_repository=agente_facial_repository
    )

    # CADASTRAR FOTO
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
        
        
# ATUALIZAR FOTO FACIAL
@router.put(
    "/{agente_id}/foto",
    response_model=FotoResponse
)
def atualizar_foto_facial(
    agente_id: UUID,
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    # AGENTE só pode alterar a própria foto.
    # ADMIN pode alterar a foto de qualquer agente.

    if (
        agente_atual.perfil != "ADMIN"
        and agente_atual.id != agente_id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "Você só pode atualizar "
                "sua própria foto facial."
            )
        )

    foto_repository = FotoRepository(db)

    embedding_service = EmbeddingService()

    embedding_repository = EmbeddingRepository(db)

    agente_facial_repository = AgenteFacialRepository(db)

    service = FotoService(
        repository=foto_repository,
        embedding_service=embedding_service,
        embedding_repository=embedding_repository,
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


@router.get(
    "/{agente_id}/foto"
)
def carregar_foto_agente(
    agente_id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    repository = FotoRepository(db)

    foto = repository.buscar_mais_recente_por_agente(
        agente_id
    )

    # AGENTE NÃO POSSUI FOTO
    if not foto:
        return Response(status_code=204)

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

# EXCLUIR AGENTE
@router.delete(
    "/{id}",
    status_code=204
)
def deletar_agente(
    id: UUID,
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_admin_atual)
):

    repository = AgenteRepository(db)

    service = AgenteService(repository)

    try:

        service.deletar(id)

    except ValueError as erro:

        raise HTTPException(
            status_code=404,
            detail=str(erro)
        )