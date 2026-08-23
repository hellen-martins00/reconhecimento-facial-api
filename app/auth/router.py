from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile
)

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.agentes.repository import AgenteRepository
from app.agentes_faciais.repository import AgenteFacialRepository

from app.auth.facial_service import LoginFacialService

from app.auth.schema import (
    LoginRequest,
    LoginResponse,
    LoginFacialResponse
)

from app.auth.service import AuthService


router = APIRouter(
    prefix="/login",
    tags=["Autenticação"]
)


# LOGIN COM USUÁRIO E SENHA

@router.post(
    "",
    response_model=LoginResponse
)
def login(
    dados: LoginRequest,
    db: Session = Depends(get_db)
):

    repository = AgenteRepository(db)

    service = AuthService(repository)

    try:

        return service.login(
            dados.usuario,
            dados.senha
        )

    except ValueError as erro:

        raise HTTPException(
            status_code=401,
            detail=str(erro)
        )


# LOGIN POR RECONHECIMENTO FACIAL

@router.post(
    "/facial",
    response_model=LoginFacialResponse
)
def login_facial(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    extensao = Path(
        arquivo.filename
    ).suffix.lower()

    extensoes_permitidas = {
        ".jpg",
        ".jpeg",
        ".png"
    }

    if extensao not in extensoes_permitidas:

        raise HTTPException(
            status_code=400,
            detail=(
                "Formato de imagem não permitido. "
                "Use JPG, JPEG ou PNG."
            )
        )

    # Ler imagem diretamente para memória
    conteudo = arquivo.file.read()

    if not conteudo:

        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio."
        )

    try:

        repository = AgenteFacialRepository(
            db
        )

        service = LoginFacialService(
            repository
        )

        resultado = service.autenticar(
            conteudo
        )

        # NÃO RECONHECIDO

        if not resultado["autenticado"]:

            return {
                "autenticado": False,
                "distancia": resultado["distancia"],
                "access_token": None,
                "token_type": None,
                "id": None,
                "nome": None,
                "usuario": None,
                "perfil": None
            }

        # RECONHECIDO

        agente = resultado["agente"]

        return {
            "autenticado": True,
            "distancia": resultado["distancia"],
            "access_token": resultado["access_token"],
            "token_type": "bearer",
            "id": agente.id,
            "nome": agente.nome,
            "usuario": agente.usuario,
            "perfil": agente.perfil
        }

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )