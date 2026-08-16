from app.database import SessionLocal

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.passagens.model import PassagemCriminal
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial

from app.embeddings.service import EmbeddingService
from app.embeddings.repository import EmbeddingRepository


print("Iniciando teste de embedding + banco...")

db = SessionLocal()

try:

    # 1. Buscar uma foto cadastrada
    foto = db.query(Foto).first()

    if not foto:
        raise ValueError(
            "Nenhuma foto cadastrada no banco. "
            "Cadastre uma foto antes de executar este teste."
        )

    print("Foto encontrada!")
    print(f"ID: {foto.id}")
    print(f"Caminho: {foto.caminho}")

    # 2. Gerar embedding
    service = EmbeddingService()

    vetor = service.gerar_embedding(foto.caminho)

    print("Embedding gerado!")
    print(f"Dimensões: {len(vetor)}")

    # 3. Salvar embedding no banco
    repository = EmbeddingRepository(db)

    embedding = repository.salvar(
        foto_id=foto.id,
        vetor=vetor
    )

    print("Embedding salvo no banco!")
    print(f"ID do embedding: {embedding.id}")
    print(f"ID da foto: {embedding.foto_id}")
    print(f"Dimensões do vetor: {len(embedding.vetor)}")

finally:
    db.close()