
from datetime import date, timedelta
from types import SimpleNamespace
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.desaparecimentos.schema import (
    RegistroDesaparecimentoCreate,
    RegistroDesaparecimentoUpdate,
)
from app.desaparecimentos.service import (
    RegistroDesaparecimentoService,
)


# --------------------------------------------------
# TESTES DOS SCHEMAS
# --------------------------------------------------

def dados_validos():
    return {
        "pessoa_id": uuid4(),
        "data_desaparecimento": date.today() - timedelta(days=1),
        "local_desaparecimento": "Brasília - DF",
        "descricao": "Desaparecimento registrado para teste.",
        "status": "DESAPARECIDO",
    }


def test_schema_criar_registro_com_dados_validos():
    dados = RegistroDesaparecimentoCreate(**dados_validos())

    assert dados.status == "DESAPARECIDO"
    assert dados.local_desaparecimento == "Brasília - DF"


def test_schema_status_padrao_desaparecido():
    dados = dados_validos()
    dados.pop("status")

    registro = RegistroDesaparecimentoCreate(**dados)

    assert registro.status == "DESAPARECIDO"


def test_schema_rejeita_data_futura():
    dados = dados_validos()
    dados["data_desaparecimento"] = date.today() + timedelta(days=1)

    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(**dados)


@pytest.mark.parametrize(
    "local",
    ["", "AB", "A" * 201],
)
def test_schema_rejeita_local_invalido(local):
    dados = dados_validos()
    dados["local_desaparecimento"] = local

    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(**dados)


@pytest.mark.parametrize(
    "descricao",
    ["", "AB", "A" * 501],
)
def test_schema_rejeita_descricao_invalida(descricao):
    dados = dados_validos()
    dados["descricao"] = descricao

    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(**dados)


def test_schema_remove_espacos_do_local_e_descricao():
    dados = dados_validos()
    dados["local_desaparecimento"] = "  Brasília - DF  "
    dados["descricao"] = "  Pessoa desaparecida para teste.  "

    registro = RegistroDesaparecimentoCreate(**dados)

    assert registro.local_desaparecimento == "Brasília - DF"
    assert registro.descricao == "Pessoa desaparecida para teste."


def test_schema_rejeita_status_invalido():
    dados = dados_validos()
    dados["status"] = "EM_ANALISE"

    with pytest.raises(ValidationError):
        RegistroDesaparecimentoCreate(**dados)


def test_schema_update_rejeita_data_futura():
    with pytest.raises(ValidationError):
        RegistroDesaparecimentoUpdate(
            data_desaparecimento=date.today() + timedelta(days=1)
        )


# --------------------------------------------------
# TESTES DO SERVICE
# --------------------------------------------------

@pytest.fixture
def repository():
    return Mock()


@pytest.fixture
def service(repository):
    return RegistroDesaparecimentoService(repository)


def test_criar_registro_com_pessoa_existente(service, repository):
    pessoa_id = uuid4()
    repository.buscar_pessoa_por_id.return_value = SimpleNamespace(
        id=pessoa_id
    )
    repository.salvar.side_effect = lambda registro: registro

    registro = service.criar(
        pessoa_id=pessoa_id,
        data_desaparecimento=date.today(),
        local_desaparecimento="Brasília - DF",
        descricao="Registro de teste.",
    )

    assert registro.pessoa_id == pessoa_id
    assert registro.status == "DESAPARECIDO"
    repository.buscar_pessoa_por_id.assert_called_once_with(pessoa_id)
    repository.salvar.assert_called_once()


def test_criar_registro_com_pessoa_inexistente(service, repository):
    pessoa_id = uuid4()
    repository.buscar_pessoa_por_id.return_value = None

    with pytest.raises(ValueError, match="Pessoa não encontrada"):
        service.criar(
            pessoa_id=pessoa_id,
            data_desaparecimento=date.today(),
            local_desaparecimento="Brasília - DF",
            descricao="Registro de teste.",
        )

    repository.salvar.assert_not_called()


def test_listar_registros(service, repository):
    registros = [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]
    repository.listar.return_value = registros

    resultado = service.listar()

    assert resultado == registros
    repository.listar.assert_called_once()


def test_buscar_registro_existente(service, repository):
    registro_id = uuid4()
    registro = SimpleNamespace(id=registro_id)
    repository.buscar_por_id.return_value = registro

    resultado = service.buscar_por_id(registro_id)

    assert resultado == registro
    repository.buscar_por_id.assert_called_once_with(registro_id)


def test_buscar_registro_inexistente(service, repository):
    registro_id = uuid4()
    repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Registro de desaparecimento não encontrado",
    ):
        service.buscar_por_id(registro_id)


def test_listar_registros_por_pessoa(service, repository):
    pessoa_id = uuid4()
    registros = [SimpleNamespace(id=uuid4())]

    repository.buscar_pessoa_por_id.return_value = SimpleNamespace(
        id=pessoa_id
    )
    repository.listar_por_pessoa.return_value = registros

    resultado = service.listar_por_pessoa(pessoa_id)

    assert resultado == registros
    repository.listar_por_pessoa.assert_called_once_with(pessoa_id)


def test_listar_registros_de_pessoa_inexistente(service, repository):
    pessoa_id = uuid4()
    repository.buscar_pessoa_por_id.return_value = None

    with pytest.raises(ValueError, match="Pessoa não encontrada"):
        service.listar_por_pessoa(pessoa_id)

    repository.listar_por_pessoa.assert_not_called()


def test_atualizar_registro_existente(service, repository):
    registro_id = uuid4()
    registro = SimpleNamespace(
        id=registro_id,
        status="DESAPARECIDO",
        descricao="Descrição antiga.",
    )

    repository.buscar_por_id.return_value = registro
    repository.atualizar.side_effect = lambda item: item

    dados = RegistroDesaparecimentoUpdate(
        status="LOCALIZADO",
        descricao="Pessoa localizada.",
    )

    resultado = service.atualizar(registro_id, dados)

    assert resultado.status == "LOCALIZADO"
    assert resultado.descricao == "Pessoa localizada."
    repository.atualizar.assert_called_once_with(registro)


def test_atualizar_registro_inexistente(service, repository):
    registro_id = uuid4()
    repository.buscar_por_id.return_value = None

    dados = RegistroDesaparecimentoUpdate(status="LOCALIZADO")

    with pytest.raises(
        ValueError,
        match="Registro de desaparecimento não encontrado",
    ):
        service.atualizar(registro_id, dados)

    repository.atualizar.assert_not_called()


def test_deletar_registro_existente(service, repository):
    registro_id = uuid4()
    registro = SimpleNamespace(id=registro_id)
    repository.buscar_por_id.return_value = registro

    service.deletar(registro_id)

    repository.deletar.assert_called_once_with(registro)


def test_deletar_registro_inexistente(service, repository):
    registro_id = uuid4()
    repository.buscar_por_id.return_value = None

    with pytest.raises(
        ValueError,
        match="Registro de desaparecimento não encontrado",
    ):
        service.deletar(registro_id)

    repository.deletar.assert_not_called()
