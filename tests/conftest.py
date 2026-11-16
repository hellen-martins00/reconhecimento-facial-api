import os
from pathlib import Path

import pytest
from dotenv import load_dotenv

# Localiza a raiz do projeto
ROOT_DIR = Path(__file__).resolve().parents[1]

# Carrega o ambiente de testes ANTES de importar a aplicação
load_dotenv(ROOT_DIR / ".env.test", override=True)
os.environ["APP_ENV"] = "test"

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import Base, engine, SessionLocal

# Importa os modelos
from app.pessoas.model import Pessoa
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial
from app.desaparecimentos.model import RegistroDesaparecimento
from app.localizacoes.model import LocalizacaoPessoa


# Proteção para impedir execução no banco errado
assert engine.url.port == 5433, (
    f"Porta incorreta para testes: {engine.url.port}"
)

assert engine.url.database == "reconhecimento_test_db", (
    f"Banco incorreto para testes: {engine.url.database}"
)


@pytest.fixture(scope="session", autouse=True)
def criar_tabelas_teste():

    Base.metadata.create_all(bind=engine)

    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():

    session = SessionLocal()

    try:
        session.execute(
            text("""
                TRUNCATE TABLE
                    agentes_faciais,
                    agentes,
                    embeddings_faciais,
                    fotos,
                    pessoas,
                    registros_desaparecimento,
                    localizacoes_pessoa
                RESTART IDENTITY CASCADE
            """)
        )

        session.commit()

        yield session

    finally:
        session.close()