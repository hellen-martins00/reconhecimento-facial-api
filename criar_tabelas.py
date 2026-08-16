from app.database import Base, engine

# Importa todos os modelos
from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial

print("Criando tabelas...")

Base.metadata.create_all(bind=engine)

print("Tabelas criadas com sucesso!")