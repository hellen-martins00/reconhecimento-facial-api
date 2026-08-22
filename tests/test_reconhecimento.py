from types import SimpleNamespace
from unittest.mock import patch

from app.reconhecimento.service import ReconhecimentoService


def criar_service():

    repository = SimpleNamespace()

    return ReconhecimentoService(repository)


def test_reconhecimento_sem_embedding():

    repository = SimpleNamespace(
        buscar_mais_semelhante=lambda vetor: None
    )

    service = ReconhecimentoService(repository)

    with patch.object(
        service.embedding_service,
        "gerar_embedding",
        return_value=[0.1, 0.2, 0.3]
    ):

        resultado = service.reconhecer(b"imagem_teste")

    assert resultado["reconhecido"] is False
    assert resultado["distancia"] is None
    assert resultado["pessoa"] is None
    assert resultado["foto"] is None


def test_reconhecimento_distancia_acima_threshold():

    repository = SimpleNamespace(
        buscar_mais_semelhante=lambda vetor: (
            SimpleNamespace(),
            0.8
        )
    )

    service = ReconhecimentoService(repository)

    with patch.object(
        service.embedding_service,
        "gerar_embedding",
        return_value=[0.1, 0.2, 0.3]
    ):

        resultado = service.reconhecer(b"imagem_teste")

    assert resultado["reconhecido"] is False
    assert resultado["distancia"] == 0.8
    assert resultado["pessoa"] is None
    assert resultado["foto"] is None


def test_reconhecimento_sucesso():

    pessoa = SimpleNamespace(
        id="pessoa-id",
        nome="João da Silva",
        cpf="12345678901"
    )

    foto = SimpleNamespace(
        id="foto-id",
        nome_arquivo="joao.jpg",
        data_upload=None,
        pessoa=pessoa
    )

    embedding = SimpleNamespace(
        foto=foto
    )

    repository = SimpleNamespace(
        buscar_mais_semelhante=lambda vetor: (
            embedding,
            0.3
        )
    )

    service = ReconhecimentoService(repository)

    with patch.object(
        service.embedding_service,
        "gerar_embedding",
        return_value=[0.1, 0.2, 0.3]
    ):

        resultado = service.reconhecer(b"imagem_teste")

    assert resultado["reconhecido"] is True
    assert resultado["distancia"] == 0.3

    assert resultado["pessoa"] == pessoa
    assert resultado["foto"] == foto