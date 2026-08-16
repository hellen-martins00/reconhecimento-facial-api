from app.database import SessionLocal

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.enderecos.model import Endereco
from app.fotos.model import Foto
from app.embeddings.model import EmbeddingFacial
from app.passagens.model import PassagemCriminal

from app.embeddings.model import EmbeddingFacial


print("Testando relacionamento Embedding → Foto → Pessoa...")

db = SessionLocal()

try:

    embedding = (
        db.query(EmbeddingFacial)
        .first()
    )

    if not embedding:
        raise ValueError(
            "Nenhum embedding encontrado no banco."
        )

    print()
    print("Embedding encontrado!")
    print(f"Embedding ID: {embedding.id}")

    foto = embedding.foto

    if not foto:
        raise ValueError(
            "O embedding não possui uma foto relacionada."
        )

    print()
    print("Foto encontrada!")
    print(f"Foto ID: {foto.id}")
    print(f"Nome arquivo: {foto.nome_arquivo}")

    pessoa = foto.pessoa

    if not pessoa:
        raise ValueError(
            "A foto não possui uma pessoa relacionada."
        )

    print()
    print("Pessoa encontrada!")
    print(f"Pessoa ID: {pessoa.id}")
    print(f"Nome: {pessoa.nome}")
    print(f"CPF: {pessoa.cpf}")

finally:

    db.close()