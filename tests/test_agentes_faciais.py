from types import SimpleNamespace
from unittest.mock import patch
from uuid import uuid4

from app.agentes_faciais.service import AgenteFacialService


def test_cadastrar_agente_facial_sucesso():

    agente_id = uuid4()

    vetor_gerado = [0.1, 0.2, 0.3]

    agente_facial_salvo = SimpleNamespace(
        agente_id=agente_id,
        vetor=vetor_gerado
    )

    repository = SimpleNamespace(
        buscar_por_agente_id=lambda agente_id: None,
        salvar=lambda agente_facial: agente_facial
    )

    service = AgenteFacialService(repository)

    with patch.object(
        service.embedding_service,
        "gerar_embedding",
        return_value=vetor_gerado
    ):

        resultado = service.cadastrar(
            agente_id,
            b"imagem_teste"
        )

    assert resultado.agente_id == agente_id
    assert resultado.vetor == vetor_gerado


def test_nao_pode_cadastrar_dois_cadastros_faciais():

    agente_id = uuid4()

    cadastro_existente = SimpleNamespace(
        agente_id=agente_id,
        vetor=[0.1, 0.2, 0.3]
    )

    repository = SimpleNamespace(
        buscar_por_agente_id=lambda agente_id: cadastro_existente,
        salvar=lambda agente_facial: agente_facial
    )

    service = AgenteFacialService(repository)

    try:

        service.cadastrar(
            agente_id,
            b"imagem_teste"
        )

        assert False, (
            "Era esperado ValueError para agente "
            "que já possui cadastro facial."
        )

    except ValueError as erro:

        assert str(erro) == (
            "Este agente já possui um cadastro facial."
        )


def test_cadastrar_gera_embedding_com_conteudo_da_imagem():

    agente_id = uuid4()

    vetor_gerado = [0.5, 0.6, 0.7]

    repository = SimpleNamespace(
        buscar_por_agente_id=lambda agente_id: None,
        salvar=lambda agente_facial: agente_facial
    )

    service = AgenteFacialService(repository)

    conteudo = b"imagem_teste"

    with patch.object(
        service.embedding_service,
        "gerar_embedding",
        return_value=vetor_gerado
    ) as gerar_embedding_mock:

        resultado = service.cadastrar(
            agente_id,
            conteudo
        )

    gerar_embedding_mock.assert_called_once_with(
        conteudo
    )

    assert resultado.vetor == vetor_gerado
    assert resultado.agente_id == agente_id