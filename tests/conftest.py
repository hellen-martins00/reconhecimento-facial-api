import pytest

from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app
from app.database import Base, engine, SessionLocal

# Importa todos os modelos para o SQLAlchemy conhecer
# todas as tabelas antes do create_all
from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial


@pytest.fixture(scope="session", autouse=True)
def criar_tabelas_teste():
    """
    Cria todas as tabelas no banco exclusivo de testes.
    """

    Base.metadata.create_all(bind=engine)

    yield


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def db():
    """
    Cria uma sessão limpa para cada teste.
    """

    db = SessionLocal()

    try:
        # Limpa todos os dados do banco de teste antes
        # de cada teste.
        #
        # CASCADE remove também os registros relacionados
        # por chaves estrangeiras.
        db.execute(
            text("""
                TRUNCATE TABLE
                    agentes_faciais,
                    agentes,
                    embeddings_faciais,
                    fotos,
                    telefones,
                    enderecos,
                    passagens_criminais,
                    pessoas
                RESTART IDENTITY CASCADE
            """)
        )

        db.commit()

        yield db

    finally:
        db.close()