from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial

from app.pessoas.router import router as pessoa_router
from app.telefones.router import router as telefone_router
from app.enderecos.router import router as endereco_router
from app.fotos.router import router as foto_router
from app.reconhecimento.router import router as reconhecimento_router
from app.passagens.router import router as passagem_router
from app.agentes.router import router as agente_router
from app.auth.router import router as auth_router


from contextlib import asynccontextmanager
from deepface import DeepFace

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Carrega o modelo na memória assim que o servidor liga no Railway
    print("Pre-carregando modelos faciais...")
    try:
        DeepFace.build_model("Facenet")
        # Força o download do detector RetinaFace no boot
        DeepFace.extract_faces(img_path="https://raw.githubusercontent.com/serengil/deepface/master/tests/dataset/img1.jpg", detector_backend="retinaface")
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


app.include_router(pessoa_router)
app.include_router(telefone_router)
app.include_router(endereco_router)
app.include_router(foto_router)
app.include_router(reconhecimento_router)
app.include_router(passagem_router)
app.include_router(agente_router)
app.include_router(auth_router)
