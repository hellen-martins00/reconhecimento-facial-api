from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4
import importlib

import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from app.desaparecimentos.model import RegistroDesaparecimento
from app.desaparecimentos.repository import (
    RegistroDesaparecimentoRepository,
)
from app.desaparecimentos.schema import (
    RegistroDesaparecimentoCreate,
    RegistroDesaparecimentoUpdate,
    RegistroDesaparecimentoResponse,
)
from app.desaparecimentos.service import (
    RegistroDesaparecimentoService,
)

router = importlib.import_module("app.desaparecimentos.router")


# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def pessoa_id():
    return uuid4()


@pytest.fixture
def registro_id():
    return uuid4()


@pytest.fixture
def registro(pessoa_id, registro_id):
    return RegistroDesaparecimento(
        id=registro_id,
        pessoa_id=pessoa_id,
        data_desaparecimento=date(2025, 10, 10),
        local_desaparecimento="Brasília - DF",
        descricao="Desaparecimento para teste",
        status="DESAPARECIDO",
    )


@pytest.fixture
def repository(db):
    return RegistroDesaparecimentoRepository(db)


@pytest.fixture
def dados_criacao(pessoa_id):
    return RegistroDesaparecimentoCreate(
        pessoa_id=pessoa_id,
        data_desaparecimento=date(2025, 10, 10),
        local_desaparecimento="Brasília - DF",
        descricao="Desaparecimento para teste",
    )


# ==========================================================
# TESTES DO REPOSITORY
# ==========================================================

def test_salvar_registro(repository, db, registro):
    resultado = repository.salvar(registro)

    db.add.assert_called_once_with(registro)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(registro)

    assert resultado is registro


def test_salvar_faz_rollback_quando_ocorre_erro(
    repository,
    db,
    registro,
):
    db.commit.side_effect = Exception("Erro no banco")

    with pytest.raises(Exception, match="Erro no banco"):
        repository.salvar(registro)

    db.add.assert_called_once_with(registro)
    db.rollback.assert_called_once()


def test_buscar_por_id_encontrado(repository, db, registro):
    db.query.return_value.filter.return_value.first.return_value = registro

    resultado = repository.buscar_por_id(registro.id)

    db.query.assert_called_once_with(RegistroDesaparecimento)
    assert resultado is registro


def test_buscar_por_id_nao_encontrado(repository, db):
    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_id(uuid4())

    assert resultado is None


def test_listar_registros(repository, db, registro):
    registros = [registro]
    db.query.return_value.all.return_value = registros

    resultado = repository.listar()

    db.query.assert_called_once_with(RegistroDesaparecimento)
    assert resultado == registros


def test_listar_sem_registros(repository, db):
    db.query.return_value.all.return_value = []

    resultado = repository.listar()

    assert resultado == []


def test_listar_por_pessoa(repository, db, registro, pessoa_id):
    registros = [registro]
    db.query.return_value.filter.return_value.all.return_value = registros

    resultado = repository.listar_por_pessoa(pessoa_id)

    db.query.assert_called_once_with(RegistroDesaparecimento)
    assert resultado == registros


def test_listar_por_pessoa_sem_registros(repository, db, pessoa_id):
    db.query.return_value.filter.return_value.all.return_value = []

    resultado = repository.listar_por_pessoa(pessoa_id)

    assert resultado == []


def test_buscar_pessoa_por_id_encontrada(repository, db, pessoa_id):
    pessoa = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = pessoa

    resultado = repository.buscar_pessoa_por_id(pessoa_id)

    assert resultado is pessoa


def test_buscar_pessoa_por_id_nao_encontrada(repository, db, pessoa_id):
    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_pessoa_por_id(pessoa_id)

    assert resultado is None


def test_atualizar_registro(repository, db, registro):
    resultado = repository.atualizar(registro)

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(registro)

    assert resultado is registro


def test_atualizar_faz_rollback_quando_ocorre_erro(
    repository,
    db,
    registro,
):
    db.commit.side_effect = Exception("Falha ao atualizar")

    with pytest.raises(Exception, match="Falha ao atualizar"):
        repository.atualizar(registro)

    db.rollback.assert_called_once()


def test_deletar_registro(repository, db, registro):
    resultado = repository.deletar(registro)

    db.delete.assert_called_once_with(registro)
    db.commit.assert_called_once()

    assert resultado is None


def test_deletar_faz_rollback_quando_ocorre_erro(
    repository,
    db,
    registro,
):
    db.commit.side_effect = Exception("Falha ao excluir")

    with pytest.raises(Exception, match="Falha ao excluir"):
        repository.deletar(registro)

    db.delete.assert_called_once_with(registro)
    db.rollback.assert_called_once()


# ==========================================================
# TESTES DO SCHEMA - CREATE
# ==========================================================

def test_create_com_dados_validos(pessoa_id):
    dados = RegistroDesaparecimentoCreate(
        pessoa_id=pessoa_id,
        data_desaparecimento=date.today(),
        local_desaparecimento="  Brasília - DF  ",
        descricao="  Pessoa desaparecida  ",
    )

    assert dados.pessoa_id == pessoa_id
    assert dados.status == "DESAPARECIDO"
    assert dados.local_desaparecimento == "Brasília - DF"
    assert dados.descricao == "Pessoa desaparecida"


def test_create_aceita_status_localizado(pessoa_id):
    dados = RegistroDesaparecimentoCreate(
        pessoa_id=pessoa_id,
        data_desaparecimento=date.today(),
        local_desaparecimento="Brasília - DF",
        descricao="Pessoa localizada",
        status="LOCALIZADO",
    )

    assert dados.status == "LOCALIZADO"


def test_create_rejeita_data_futura(pessoa_id):
    with pytest.raises(
        ValidationError,
        match="A data do desaparecimento não pode ser futura.",
    ):
        RegistroDesaparecimentoCreate(
            pessoa_id=pessoa_id,
            data_desaparecimento=date.today() + timedelta(days=1),
            local_desaparecimento="Brasília - DF",
            descricao="Pessoa desaparecida",
        )


@pytest.mark.parametrize(
    "local",
    [
        "  ",
        "AB",
        "A" * 201,
    ],
)
def test_create_rejeita_local_com_tamanho_invalido(pessoa_id, local):
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(
            pessoa_id=pessoa_id,
            data_desaparecimento=date.today(),
            local_desaparecimento=local,
            descricao="Pessoa desaparecida",
        )


@pytest.mark.parametrize(
    "descricao",
    [
        "  ",
        "AB",
        "A" * 501,
    ],
)
def test_create_rejeita_descricao_com_tamanho_invalido(
    pessoa_id,
    descricao,
):
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(
            pessoa_id=pessoa_id,
            data_desaparecimento=date.today(),
            local_desaparecimento="Brasília - DF",
            descricao=descricao,
        )


def test_create_rejeita_status_invalido(pessoa_id):
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(
            pessoa_id=pessoa_id,
            data_desaparecimento=date.today(),
            local_desaparecimento="Brasília - DF",
            descricao="Pessoa desaparecida",
            status="EM_ANALISE",
        )


# ==========================================================
# TESTES DO SCHEMA - UPDATE
# ==========================================================

def test_update_aceita_todos_os_campos():
    dados = RegistroDesaparecimentoUpdate(
        data_desaparecimento=date(2025, 10, 10),
        local_desaparecimento="  Goiânia - GO  ",
        descricao="  Nova descrição  ",
        status="LOCALIZADO",
    )

    assert dados.data_desaparecimento == date(2025, 10, 10)
    assert dados.local_desaparecimento == "Goiânia - GO"
    assert dados.descricao == "Nova descrição"
    assert dados.status == "LOCALIZADO"


def test_update_aceita_campos_nulos():
    dados = RegistroDesaparecimentoUpdate(
        data_desaparecimento=None,
        local_desaparecimento=None,
        descricao=None,
        status=None,
    )

    assert dados.data_desaparecimento is None
    assert dados.local_desaparecimento is None
    assert dados.descricao is None
    assert dados.status is None


def test_update_rejeita_data_futura():
    with pytest.raises(
        ValidationError,
        match="A data do desaparecimento não pode ser futura.",
    ):
        RegistroDesaparecimentoUpdate(
            data_desaparecimento=date.today() + timedelta(days=1),
        )


@pytest.mark.parametrize(
    "local",
    [
        "",
        "AB",
        "A" * 201,
    ],
)
def test_update_rejeita_local_invalido(local):
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoUpdate(
            local_desaparecimento=local,
        )


def test_update_preserva_local_nulo():
    dados = RegistroDesaparecimentoUpdate(
        local_desaparecimento=None,
    )

    assert dados.local_desaparecimento is None


@pytest.mark.parametrize(
    "descricao",
    [
        "",
        "AB",
        "A" * 501,
    ],
)
def test_update_rejeita_descricao_invalida(descricao):
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoUpdate(
            descricao=descricao,
        )


def test_update_preserva_descricao_nula():
    dados = RegistroDesaparecimentoUpdate(
        descricao=None,
    )

    assert dados.descricao is None


def test_update_rejeita_status_invalido():
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoUpdate(
            status="EM_ANALISE",
        )


# ==========================================================
# TESTES DO SCHEMA - RESPONSE
# ==========================================================

def test_response_com_dados_validos(pessoa_id, registro_id):
    agora = datetime.now()

    resposta = RegistroDesaparecimentoResponse(
        id=registro_id,
        pessoa_id=pessoa_id,
        data_desaparecimento=date(2025, 10, 10),
        local_desaparecimento="Brasília - DF",
        descricao="Pessoa desaparecida",
        status="DESAPARECIDO",
        created_at=agora,
        updated_at=agora,
    )

    assert resposta.id == registro_id
    assert resposta.pessoa_id == pessoa_id
    assert resposta.status == "DESAPARECIDO"


def test_response_from_attributes(registro):
    registro.created_at = datetime.now()
    registro.updated_at = datetime.now()

    resposta = RegistroDesaparecimentoResponse.model_validate(
        registro,
        from_attributes=True,
    )

    assert resposta.id == registro.id
    assert resposta.pessoa_id == registro.pessoa_id
    assert resposta.local_desaparecimento == registro.local_desaparecimento


# ==========================================================
# TESTES DO ROUTER
# ==========================================================

@pytest.fixture
def service_mock():
    return MagicMock()


@pytest.fixture
def agente_atual():
    return SimpleNamespace(
        id=uuid4(),
        nome="Agente de teste",
        usuario="agente.teste",
        perfil="AGENTE",
    )


def test_obter_service(db):
    with patch.object(
        router,
        "RegistroDesaparecimentoRepository",
    ) as repository_mock, patch.object(
        router,
        "RegistroDesaparecimentoService",
    ) as service_class_mock:

        resultado = router.obter_service(db)

        repository_mock.assert_called_once_with(db)
        service_class_mock.assert_called_once_with(
            repository_mock.return_value
        )

        assert resultado is service_class_mock.return_value


def test_criar_registro_sucesso(
    db,
    agente_atual,
    dados_criacao,
    service_mock,
):
    esperado = MagicMock()
    service_mock.criar.return_value = esperado

    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.criar_registro(
            dados_criacao,
            db,
            agente_atual,
        )

    service_mock.criar.assert_called_once_with(
        pessoa_id=dados_criacao.pessoa_id,
        data_desaparecimento=dados_criacao.data_desaparecimento,
        local_desaparecimento=dados_criacao.local_desaparecimento,
        descricao=dados_criacao.descricao,
        status=dados_criacao.status,
    )

    assert resultado is esperado


def test_criar_registro_pessoa_nao_encontrada(
    db,
    agente_atual,
    dados_criacao,
    service_mock,
):
    service_mock.criar.side_effect = ValueError("Pessoa não encontrada.")

    with patch.object(router, "obter_service", return_value=service_mock):
        with pytest.raises(HTTPException) as erro:
            router.criar_registro(
                dados_criacao,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == "Pessoa não encontrada."


def test_listar_registros(db, agente_atual, service_mock):
    esperado = [MagicMock(), MagicMock()]
    service_mock.listar.return_value = esperado

    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.listar_registros(db, agente_atual)

    service_mock.listar.assert_called_once()
    assert resultado == esperado


def test_obter_estatisticas(db, agente_atual):
    estatisticas = SimpleNamespace(
        casos_em_aberto=5,
        pessoas_localizadas=3,
    )
    db.query.return_value.one.return_value = estatisticas

    resultado = router.obter_estatisticas(db, agente_atual)

    assert resultado == {
        "casos_em_aberto": 5,
        "pessoas_localizadas": 3,
    }
    db.query.assert_called_once()
    db.query.return_value.one.assert_called_once()


def test_listar_por_pessoa_sucesso(
    db,
    agente_atual,
    pessoa_id,
    service_mock,
):
    esperado = [MagicMock()]
    service_mock.listar_por_pessoa.return_value = esperado

    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.listar_por_pessoa(
            pessoa_id,
            db,
            agente_atual,
        )

    service_mock.listar_por_pessoa.assert_called_once_with(pessoa_id)
    assert resultado == esperado


def test_listar_por_pessoa_nao_encontrada(
    db,
    agente_atual,
    pessoa_id,
    service_mock,
):
    service_mock.listar_por_pessoa.side_effect = ValueError(
        "Pessoa não encontrada."
    )

    with patch.object(router, "obter_service", return_value=service_mock):
        with pytest.raises(HTTPException) as erro:
            router.listar_por_pessoa(
                pessoa_id,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == "Pessoa não encontrada."


def test_buscar_registro_sucesso(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    esperado = MagicMock()
    service_mock.buscar_por_id.return_value = esperado

    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.buscar_registro(
            registro_id,
            db,
            agente_atual,
        )

    service_mock.buscar_por_id.assert_called_once_with(registro_id)
    assert resultado is esperado


def test_buscar_registro_nao_encontrado(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    service_mock.buscar_por_id.side_effect = ValueError(
        "Registro de desaparecimento não encontrado."
    )

    with patch.object(router, "obter_service", return_value=service_mock):
        with pytest.raises(HTTPException) as erro:
            router.buscar_registro(
                registro_id,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == (
        "Registro de desaparecimento não encontrado."
    )


def test_atualizar_registro_sucesso(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    dados = RegistroDesaparecimentoUpdate(
        status="LOCALIZADO",
    )
    esperado = MagicMock()
    service_mock.atualizar.return_value = esperado

    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.atualizar_registro(
            registro_id,
            dados,
            db,
            agente_atual,
        )

    service_mock.atualizar.assert_called_once_with(
        id=registro_id,
        dados=dados,
    )
    assert resultado is esperado


def test_atualizar_registro_nao_encontrado(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    dados = RegistroDesaparecimentoUpdate(
        status="LOCALIZADO",
    )
    service_mock.atualizar.side_effect = ValueError(
        "Registro de desaparecimento não encontrado."
    )

    with patch.object(router, "obter_service", return_value=service_mock):
        with pytest.raises(HTTPException) as erro:
            router.atualizar_registro(
                registro_id,
                dados,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404


def test_deletar_registro_sucesso(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    with patch.object(router, "obter_service", return_value=service_mock):
        resultado = router.deletar_registro(
            registro_id,
            db,
            agente_atual,
        )

    service_mock.deletar.assert_called_once_with(registro_id)
    assert resultado is None


def test_deletar_registro_nao_encontrado(
    db,
    agente_atual,
    registro_id,
    service_mock,
):
    service_mock.deletar.side_effect = ValueError(
        "Registro de desaparecimento não encontrado."
    )

    with patch.object(router, "obter_service", return_value=service_mock):
        with pytest.raises(HTTPException) as erro:
            router.deletar_registro(
                registro_id,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == (
        "Registro de desaparecimento não encontrado."
    )