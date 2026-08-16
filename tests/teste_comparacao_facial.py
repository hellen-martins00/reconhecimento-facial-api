from app.database import SessionLocal

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal

from app.embeddings.repository import EmbeddingRepository
from app.embeddings.service import EmbeddingService

print("Iniciando teste de comparação facial...")

db = SessionLocal()

try:

    caminho_imagem = "tests/imagens/outra_pessoa.jpeg"

    print("Gerando embedding da nova foto...")

    service = EmbeddingService()

    vetor = service.gerar_embedding(
        caminho_imagem
    )

    print("Embedding gerado!")
    print(f"Dimensões: {len(vetor)}")

    repository = EmbeddingRepository(db)

    resultado = repository.buscar_mais_semelhante(
        vetor
    )

    if not resultado:
        raise ValueError(
            "Nenhum embedding encontrado no banco."
        )

    embedding, distancia = resultado

    print()
    print("Embedding mais semelhante encontrado!")
    print(f"ID do embedding: {embedding.id}")
    print(f"ID da foto: {embedding.foto_id}")
    print(f"Distância: {distancia}")

finally:

    db.close()