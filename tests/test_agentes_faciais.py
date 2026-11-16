from datetime import datetime
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import MagicMock, patch

import pytest

from app.agentes_faciais.model import AgenteFacial
from app.agentes_faciais.repository import AgenteFacialRepository
from app.agentes_faciais.schema import AgenteFacialResponse
from app.agentes_faciais.service import AgenteFacialService


# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def agente_id():
    return uuid4()


@pytest.fixture
def agente_facial(agente_id):
    return AgenteFacial(
        id=uuid4(),
        agente_id=agente_id,
        vetor=[0.1] * 512,
    )


@pytest.fixture
def repository(db):
    return AgenteFacialRepository(db)


@pytest.fixture
def service(repository):
    # Transforma os métodos do repositório em mocks
    # apenas nos testes que utilizam o service.
    repository.buscar_por_agente_id = MagicMock()
    repository.buscar_por_id = MagicMock()
    repository.buscar_mais_semelhante = MagicMock()
    repository.salvar = MagicMock()

    with patch(
        "app.agentes_faciais.service.EmbeddingService"
    ) as embedding_service:

        embedding_service.return_value.gerar_embedding.return_value = [
            0.1
        ] * 512

        instancia = AgenteFacialService(repository)

        yield instancia

# ==========================================================
# TESTES DO REPOSITORY
# ==========================================================

def test_salvar_agente_facial(repository, db, agente_facial):
    resultado = repository.salvar(agente_facial)

    db.add.assert_called_once_with(agente_facial)
    db.flush.assert_called_once()
    db.refresh.assert_called_once_with(agente_facial)

    assert resultado is agente_facial


def test_buscar_por_agente_id_encontrado(
    repository,
    db,
    agente_facial,
    agente_id,
):
    db.query.return_value.filter.return_value.first.return_value = (
        agente_facial
    )

    resultado = repository.buscar_por_agente_id(agente_id)

    db.query.assert_called_once_with(AgenteFacial)
    assert resultado is agente_facial


def test_buscar_por_agente_id_nao_encontrado(
    repository,
    db,
    agente_id,
):
    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_agente_id(agente_id)

    assert resultado is None


def test_buscar_por_id_encontrado(
    repository,
    db,
    agente_facial,
):
    db.query.return_value.filter.return_value.first.return_value = (
        agente_facial
    )

    resultado = repository.buscar_por_id(agente_facial.id)

    db.query.assert_called_once_with(AgenteFacial)
    assert resultado is agente_facial


def test_buscar_por_id_nao_encontrado(
    repository,
    db,
):
    identificador = uuid4()

    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_id(identificador)

    assert resultado is None


def test_buscar_mais_semelhante_sem_excluir_agente(
    repository,
    db,
):
    vetor = [0.2] * 512
    esperado = (MagicMock(), 0.25)

    consulta = db.query.return_value
    consulta.order_by.return_value.first.return_value = esperado

    resultado = repository.buscar_mais_semelhante(vetor)

    db.query.assert_called_once()
    consulta.filter.assert_not_called()
    consulta.order_by.assert_called_once()

    assert resultado == esperado


def test_buscar_mais_semelhante_excluindo_agente(
    repository,
    db,
):
    vetor = [0.2] * 512
    agente_id_excluir = uuid4()
    esperado = (MagicMock(), 0.35)

    consulta = db.query.return_value
    consulta.filter.return_value = consulta
    consulta.order_by.return_value.first.return_value = esperado

    resultado = repository.buscar_mais_semelhante(
        vetor,
        agente_id_excluir=agente_id_excluir,
    )

    consulta.filter.assert_called_once()
    consulta.order_by.assert_called_once()

    assert resultado == esperado


def test_buscar_mais_semelhante_sem_resultado(
    repository,
    db,
):
    vetor = [0.2] * 512

    consulta = db.query.return_value
    consulta.order_by.return_value.first.return_value = None

    resultado = repository.buscar_mais_semelhante(vetor)

    assert resultado is None


# ==========================================================
# TESTES DO SCHEMA
# ==========================================================

def test_agente_facial_response():
    identificador = uuid4()
    agente_id = uuid4()
    data_criacao = datetime(2026, 1, 15, 10, 30, 0)

    resposta = AgenteFacialResponse(
        id=identificador,
        agente_id=agente_id,
        created_at=data_criacao,
    )

    assert resposta.id == identificador
    assert resposta.agente_id == agente_id
    assert resposta.created_at == data_criacao


def test_agente_facial_response_from_attributes():
    identificador = uuid4()
    agente_id = uuid4()
    data_criacao = datetime(2026, 1, 15, 10, 30, 0)

    objeto = SimpleNamespace(
        id=identificador,
        agente_id=agente_id,
        created_at=data_criacao,
    )

    resposta = AgenteFacialResponse.model_validate(
        objeto,
        from_attributes=True,
    )

    assert resposta.id == identificador
    assert resposta.agente_id == agente_id
    assert resposta.created_at == data_criacao


def test_agente_facial_response_rejeita_dados_invalidos():
    with pytest.raises(Exception):
        AgenteFacialResponse(
            id="id-invalido",
            agente_id="agente-invalido",
            created_at="data-invalida",
        )


# ==========================================================
# TESTES DO SERVICE
# ==========================================================

def test_verificar_rosto_duplicado_sem_resultado(service, repository):
    repository.buscar_mais_semelhante.return_value = None

    service._verificar_rosto_duplicado([0.1] * 512)

    repository.buscar_mais_semelhante.assert_called_once_with(
        [0.1] * 512,
        agente_id_excluir=None,
    )


def test_verificar_rosto_duplicado_com_distancia_abaixo_do_limite(
    service,
    repository,
):
    agente_facial_existente = MagicMock()

    repository.buscar_mais_semelhante.return_value = (
        agente_facial_existente,
        0.3,
    )

    with pytest.raises(
        ValueError,
        match="Esta foto facial já está cadastrada para outro agente.",
    ):
        service._verificar_rosto_duplicado([0.1] * 512)


def test_verificar_rosto_duplicado_com_distancia_igual_ao_limite(
    service,
    repository,
):
    repository.buscar_mais_semelhante.return_value = (
        MagicMock(),
        0.5,
    )

    with pytest.raises(ValueError):
        service._verificar_rosto_duplicado([0.1] * 512)


def test_verificar_rosto_duplicado_com_distancia_acima_do_limite(
    service,
    repository,
):
    repository.buscar_mais_semelhante.return_value = (
        MagicMock(),
        0.7,
    )

    service._verificar_rosto_duplicado([0.1] * 512)


def test_verificar_rosto_duplicado_exclui_agente_atual(
    service,
    repository,
):
    agente_id = uuid4()
    vetor = [0.1] * 512

    repository.buscar_mais_semelhante.return_value = None

    service._verificar_rosto_duplicado(
        vetor,
        agente_id_atual=agente_id,
    )

    repository.buscar_mais_semelhante.assert_called_once_with(
        vetor,
        agente_id_excluir=agente_id,
    )


def test_cadastrar_agente_facial_com_sucesso(
    service,
    repository,
    agente_id,
):
    conteudo = b"imagem facial"
    vetor = [0.1] * 512
    esperado = MagicMock()

    repository.buscar_por_agente_id.return_value = None
    repository.buscar_mais_semelhante.return_value = None
    repository.salvar.return_value = esperado

    service.embedding_service.gerar_embedding.return_value = vetor

    resultado = service.cadastrar(agente_id, conteudo)

    service.embedding_service.gerar_embedding.assert_called_once_with(
        conteudo
    )

    repository.buscar_por_agente_id.assert_called_once_with(
        agente_id
    )

    repository.buscar_mais_semelhante.assert_called_once_with(
        vetor,
        agente_id_excluir=None,
    )

    repository.salvar.assert_called_once()

    agente_salvo = repository.salvar.call_args.args[0]

    assert isinstance(agente_salvo, AgenteFacial)
    assert agente_salvo.agente_id == agente_id
    assert agente_salvo.vetor == vetor
    assert resultado is esperado


def test_cadastrar_agente_que_ja_possui_cadastro_facial(
    service,
    repository,
    agente_id,
):
    repository.buscar_por_agente_id.return_value = MagicMock()

    with pytest.raises(
        ValueError,
        match="Este agente já possui um cadastro facial.",
    ):
        service.cadastrar(agente_id, b"imagem facial")

    service.embedding_service.gerar_embedding.assert_not_called()
    repository.salvar.assert_not_called()


def test_cadastrar_rosto_que_ja_pertence_a_outro_agente(
    service,
    repository,
    agente_id,
):
    repository.buscar_por_agente_id.return_value = None
    repository.buscar_mais_semelhante.return_value = (
        MagicMock(),
        0.2,
    )

    with pytest.raises(
        ValueError,
        match="Esta foto facial já está cadastrada para outro agente.",
    ):
        service.cadastrar(agente_id, b"imagem facial")

    repository.salvar.assert_not_called()