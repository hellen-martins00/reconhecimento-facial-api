from io import BytesIO
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

import pytest

from app.fotos.service import FotoService

class ArquivoFake:

    def __init__(self, nome, conteudo):
        self.filename = nome
        self.file = BytesIO(conteudo)


def criar_service():

    repository = Mock()
    embedding_service = Mock()
    embedding_repository = Mock()

    service = FotoService(
        repository=repository,
        embedding_service=embedding_service,
        embedding_repository=embedding_repository
    )

    return (
        service,
        repository,
        embedding_service,
        embedding_repository
    )


# UPLOAD / REGISTRO
def test_upload_foto_sucesso():

    pessoa_id = uuid4()
    foto_id = uuid4()

    conteudo = b"imagem_teste"

    pessoa = SimpleNamespace(
        id=pessoa_id
    )

    foto_salva = SimpleNamespace(
        id=foto_id,
        pessoa_id=pessoa_id,
        nome_arquivo="foto.jpg",
        arquivo=conteudo
    )

    service, repository, embedding_service, embedding_repository = (
        criar_service()
    )

    # Simula a consulta da pessoa
    repository.db.query.return_value.filter.return_value.first.return_value = (
        pessoa
    )

    # Simula salvar foto
    repository.salvar.return_value = foto_salva

    # Simula geração do embedding
    vetor = [0.1, 0.2, 0.3]

    embedding_service.gerar_embedding.return_value = vetor

    arquivo = ArquivoFake(
        "foto.jpg",
        conteudo
    )

    resultado = service.criar(
        pessoa_id,
        arquivo
    )

    assert resultado == foto_salva

    repository.salvar.assert_called_once()

    embedding_service.gerar_embedding.assert_called_once_with(
        conteudo
    )

    embedding_repository.salvar.assert_called_once_with(
        foto_id=foto_id,
        vetor=vetor
    )

    repository.db.commit.assert_called_once()


def test_upload_falha_se_pessoa_nao_existir():

    pessoa_id = uuid4()

    service, repository, _, _ = criar_service()

    repository.db.query.return_value.filter.return_value.first.return_value = (
        None
    )

    arquivo = ArquivoFake(
        "foto.jpg",
        b"imagem_teste"
    )

    with pytest.raises(ValueError) as erro:

        service.criar(
            pessoa_id,
            arquivo
        )

    assert str(erro.value) == "Pessoa não encontrada."


def test_upload_rejeita_extensao_invalida():

    pessoa_id = uuid4()

    pessoa = SimpleNamespace(
        id=pessoa_id
    )

    service, repository, _, _ = criar_service()

    repository.db.query.return_value.filter.return_value.first.return_value = (
        pessoa
    )

    arquivo = ArquivoFake(
        "foto.gif",
        b"imagem_teste"
    )

    with pytest.raises(ValueError) as erro:

        service.criar(
            pessoa_id,
            arquivo
        )

    assert str(erro.value) == (
        "Formato de imagem não permitido. "
        "Use JPG, JPEG ou PNG."
    )


def test_upload_rejeita_arquivo_vazio():

    pessoa_id = uuid4()

    pessoa = SimpleNamespace(
        id=pessoa_id
    )

    service, repository, _, _ = criar_service()

    repository.db.query.return_value.filter.return_value.first.return_value = (
        pessoa
    )

    arquivo = ArquivoFake(
        "foto.jpg",
        b""
    )

    with pytest.raises(ValueError) as erro:

        service.criar(
            pessoa_id,
            arquivo
        )

    assert str(erro.value) == "O arquivo enviado está vazio."


def test_upload_salva_embedding_gerado():

    pessoa_id = uuid4()
    foto_id = uuid4()

    conteudo = b"imagem_teste"
    vetor = [0.5, 0.6, 0.7]

    pessoa = SimpleNamespace(
        id=pessoa_id
    )

    foto = SimpleNamespace(
        id=foto_id,
        pessoa_id=pessoa_id
    )

    service, repository, embedding_service, embedding_repository = (
        criar_service()
    )

    repository.db.query.return_value.filter.return_value.first.return_value = (
        pessoa
    )

    repository.salvar.return_value = foto

    embedding_service.gerar_embedding.return_value = vetor

    arquivo = ArquivoFake(
        "foto.png",
        conteudo
    )

    service.criar(
        pessoa_id,
        arquivo
    )

    embedding_service.gerar_embedding.assert_called_once_with(
        conteudo
    )

    embedding_repository.salvar.assert_called_once_with(
        foto_id=foto_id,
        vetor=vetor
    )


# CONSULTA
def test_buscar_foto_sucesso():

    foto_id = uuid4()

    foto = SimpleNamespace(
        id=foto_id,
        nome_arquivo="foto.jpg"
    )

    service, repository, _, _ = criar_service()

    repository.buscar_por_id.return_value = foto

    resultado = service.buscar_por_id(
        foto_id
    )

    assert resultado == foto

    repository.buscar_por_id.assert_called_once_with(
        foto_id
    )


def test_buscar_foto_inexistente():

    foto_id = uuid4()

    service, repository, _, _ = criar_service()

    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError) as erro:

        service.buscar_por_id(
            foto_id
        )

    assert str(erro.value) == "Foto não encontrada."


def test_listar_fotos():

    foto1 = SimpleNamespace(
        id=uuid4(),
        nome_arquivo="foto1.jpg"
    )

    foto2 = SimpleNamespace(
        id=uuid4(),
        nome_arquivo="foto2.png"
    )

    fotos = [
        foto1,
        foto2
    ]

    service, repository, _, _ = criar_service()

    repository.listar.return_value = fotos

    resultado = service.listar()

    assert resultado == fotos

    repository.listar.assert_called_once()


def test_listar_fotos_por_pessoa():

    pessoa_id = uuid4()

    fotos = [
        SimpleNamespace(
            id=uuid4(),
            pessoa_id=pessoa_id
        ),
        SimpleNamespace(
            id=uuid4(),
            pessoa_id=pessoa_id
        )
    ]

    service, repository, _, _ = criar_service()

    repository.buscar_por_pessoa.return_value = fotos

    resultado = service.listar_por_pessoa(
        pessoa_id
    )

    assert resultado == fotos

    repository.buscar_por_pessoa.assert_called_once_with(
        pessoa_id
    )

# ATUALIZAÇÃO
def test_atualizar_foto_pessoa_sucesso():

    foto_id = uuid4()

    conteudo_novo = b"nova_imagem"
    vetor_novo = [0.9, 0.8, 0.7]

    foto = SimpleNamespace(
        id=foto_id,
        pessoa_id=uuid4(),
        nome_arquivo="foto_antiga.jpg",
        arquivo=b"imagem_antiga"
    )

    embedding = SimpleNamespace(
        foto_id=foto_id,
        vetor=[0.1, 0.2, 0.3]
    )

    service, repository, embedding_service, embedding_repository = (
        criar_service()
    )

    # Foto existente
    repository.buscar_por_id.return_value = foto

    # Embedding novo
    embedding_service.gerar_embedding.return_value = vetor_novo

    # Se o service buscar o embedding pelo repository,
    # simula o embedding existente.
    embedding_repository.buscar_por_foto_id.return_value = embedding

    arquivo = ArquivoFake(
        "foto_nova.png",
        conteudo_novo
    )

    resultado = service.atualizar_foto_pessoa(
        foto_id,
        arquivo
    )

    # Deve retornar a mesma foto
    assert resultado == foto

    # Deve substituir o arquivo
    assert foto.arquivo == conteudo_novo

    # Deve gerar um novo nome
    assert foto.nome_arquivo.endswith(".png")

    # Deve gerar embedding usando a nova imagem
    embedding_service.gerar_embedding.assert_called_once_with(
        conteudo_novo
    )

    # O embedding existente deve receber o novo vetor
    assert embedding.vetor == vetor_novo

    # Deve confirmar a transação
    repository.db.commit.assert_called_once()
    
    
# EXCLUSÃO
def test_deletar_foto_sucesso():

    foto_id = uuid4()

    foto = SimpleNamespace(
        id=foto_id,
        nome_arquivo="foto.jpg"
    )

    service, repository, _, _ = criar_service()

    repository.buscar_por_id.return_value = foto

    service.deletar(
        foto_id
    )

    repository.buscar_por_id.assert_called_once_with(
        foto_id
    )

    repository.deletar.assert_called_once_with(
        foto
    )


def test_deletar_foto_inexistente():

    foto_id = uuid4()

    service, repository, _, _ = criar_service()

    repository.buscar_por_id.return_value = None

    with pytest.raises(ValueError) as erro:

        service.deletar(
            foto_id
        )

    assert str(erro.value) == "Foto não encontrada."

    repository.deletar.assert_not_called()