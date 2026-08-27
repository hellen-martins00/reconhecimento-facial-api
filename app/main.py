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


app = FastAPI(
    title="API de Reconhecimento Facial",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
