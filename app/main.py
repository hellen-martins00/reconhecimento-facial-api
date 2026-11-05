# IMPORTANTE: psycopg precisa ser importado ANTES do tensorflow/deepface.
# O libpq embutido no psycopg usa seu proprio OpenSSL; se o TensorFlow carregar
# primeiro, a conexao SSL com o Postgres derruba o processo (segmentation fault).
import psycopg  # noqa: F401

import numpy as np

from contextlib import asynccontextmanager
from deepface import DeepFace

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# MODELOS
from app.pessoas.model import Pessoa
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.desaparecimentos.model import RegistroDesaparecimento
from app.localizacoes.model import LocalizacaoPessoa
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial

# ROTAS
from app.pessoas.router import router as pessoa_router
from app.fotos.router import router as foto_router
from app.reconhecimento.router import router as reconhecimento_router
from app.desaparecimentos.router import router as desaparecimentos_router
from app.localizacoes.router import router as localizacoes_router
from app.agentes.router import router as agente_router
from app.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Pre-carregando modelos faciais...")

    try:
        DeepFace.build_model("Facenet")

        dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)

        DeepFace.represent(
            img_path=dummy_img,
            model_name="Facenet",
            detector_backend="retinaface",
            enforce_detection=False
        )

        print("Modelos carregados com sucesso!")

    except Exception as e:
        print(f"Aviso no carregamento dos modelos: {e}")

    yield


app = FastAPI(
    title="API de Reconhecimento Facial",
    version="1.0.0",
    lifespan=lifespan
)


origins = [
    "https://reconhecimento-facial-front-production.up.railway.app",
    "https://reconhecimento-facial-front-production.up.railway.app/",
    "http://127.0.0.1:5173",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://localhost:3000",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# REGISTRO DAS ROTAS

app.include_router(pessoa_router)
app.include_router(foto_router)
app.include_router(reconhecimento_router)
app.include_router(desaparecimentos_router)
app.include_router(localizacoes_router)
app.include_router(agente_router)
app.include_router(auth_router)