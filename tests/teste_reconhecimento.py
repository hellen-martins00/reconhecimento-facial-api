from app.database import SessionLocal

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal

from app.embeddings.repository import EmbeddingRepository
from app.reconhecimento.service import ReconhecimentoService


print("Iniciando teste de reconhecimento facial...")

db = SessionLocal()

try:

    caminho_imagem = "tests/imagens/outra_pessoa.jpeg"

    repository = EmbeddingRepository(db)

    service = ReconhecimentoService(
        repository
    )

    resultado = service.reconhecer(
        caminho_imagem
    )

    print()
    print("Resultado do reconhecimento:")
    print(f"Reconhecido: {resultado['reconhecido']}")
    print(f"Distância: {resultado['distancia']}")

    if resultado["pessoa"]:

        pessoa = resultado["pessoa"]

        print(f"Pessoa: {pessoa.nome}")
        print(f"CPF: {pessoa.cpf}")

finally:

    db.close()