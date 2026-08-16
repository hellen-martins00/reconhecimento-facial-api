from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import Session

from app.auth.dependencies import get_agente_atual
from app.agentes.model import Agente

from app.dependencies import get_db

from app.embeddings.repository import EmbeddingRepository
from app.reconhecimento.schema import ReconhecimentoResponse
from app.reconhecimento.service import ReconhecimentoService


router = APIRouter(
    prefix="/reconhecimento",
    tags=["Reconhecimento Facial"]
)


@router.post(
    "",
    response_model=ReconhecimentoResponse
)
def reconhecer_rosto(
    arquivo: UploadFile = File(...),
    db: Session = Depends(get_db),
    agente_atual: Agente = Depends(get_agente_atual)
):

    extensao = Path(arquivo.filename).suffix.lower()

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

    # Ler a imagem diretamente para memória
    conteudo = arquivo.file.read()

    if not conteudo:

        raise HTTPException(
            status_code=400,
            detail="O arquivo enviado está vazio."
        )

    try:

        repository = EmbeddingRepository(db)

        service = ReconhecimentoService(
            repository
        )

        resultado = service.reconhecer(
            conteudo
        )

        pessoa = resultado["pessoa"]
        foto = resultado["foto"]

        if pessoa:

            resultado["pessoa"] = {
                "id": pessoa.id,
                "nome": pessoa.nome,
                "cpf": pessoa.cpf
            }

        if foto:

            resultado["foto"] = {
                "id": foto.id,
                "nome_arquivo": foto.nome_arquivo,
                "data_upload": foto.data_upload
            }

        return resultado

    except ValueError as erro:

        raise HTTPException(
            status_code=400,
            detail=str(erro)
        )