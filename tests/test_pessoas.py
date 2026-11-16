from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4
import importlib

import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from app.pessoas.model import Pessoa
from app.pessoas.repository import PessoaRepository
from app.pessoas.schema import (
    PessoaCreate,
    PessoaUpdate,
    PessoaResponse,
    PessoaListaResponse,
)
from app.pessoas.service import PessoaService

router = importlib.import_module("app.pessoas.router")


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
def pessoa(pessoa_id):
    return Pessoa(
        id=pessoa_id,
        nome="Maria da Silva",
        cpf="12345678901",
        data_nascimento=date(1990, 5, 10),
        sexo="F",
    )


@pytest.fixture
def repository(db):
    return PessoaRepository(db)


@pytest.fixture
def dados_criacao():
    return PessoaCreate(
        nome="Maria da Silva",
        cpf="12345678901",
        data_nascimento=date(1990, 5, 10),
        sexo="F",
    )


@pytest.fixture
def dados_atualizacao():
    return PessoaUpdate(
        nome="Maria Atualizada",
    )


@pytest.fixture
def agente_atual():
    return SimpleNamespace(
        id=uuid4(),
        nome="Agente de teste",
        usuario="agente.teste",
        perfil="AGENTE",
    )


@pytest.fixture
def admin_atual():
    return SimpleNamespace(
        id=uuid4(),
        nome="Administrador",
        usuario="admin",
        perfil="ADMIN",
    )


# ==========================================================
# TESTES DO REPOSITORY
# ==========================================================

def test_salvar_pessoa(repository, db, pessoa):
    resultado = repository.salvar(pessoa)

    db.add.assert_called_once_with(pessoa)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(pessoa)

    assert resultado is pessoa


def test_salvar_pessoa_faz_rollback_em_erro(repository, db, pessoa):
    db.commit.side_effect = Exception("Erro ao salvar")

    with pytest.raises(Exception, match="Erro ao salvar"):
        repository.salvar(pessoa)

    db.add.assert_called_once_with(pessoa)
    db.rollback.assert_called_once()


def test_buscar_por_cpf(repository, db, pessoa):
    db.query.return_value.filter.return_value.first.return_value = pessoa

    resultado = repository.buscar_por_cpf("12345678901")

    db.query.assert_called_once_with(Pessoa)
    assert resultado is pessoa


def test_buscar_por_cpf_nao_encontrado(repository, db):
    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_cpf("12345678901")

    assert resultado is None


def test_buscar_por_cpf_nulo(repository, db):
    resultado = repository.buscar_por_cpf(None)

    assert resultado is None
    db.query.assert_not_called()


def test_buscar_por_id(repository, db, pessoa):
    db.query.return_value.filter.return_value.first.return_value = pessoa

    resultado = repository.buscar_por_id(pessoa.id)

    db.query.assert_called_once_with(Pessoa)
    assert resultado is pessoa


def test_buscar_por_id_nao_encontrado(repository, db):
    db.query.return_value.filter.return_value.first.return_value = None

    resultado = repository.buscar_por_id(uuid4())

    assert resultado is None


def test_listar_pessoas(repository, db, pessoa):
    consulta_fotos = MagicMock()
    consulta_pessoas = MagicMock()

    subquery = MagicMock()
    subquery.c.foto_id = MagicMock()
    subquery.c.pessoa_id = MagicMock()
    subquery.c.numero = MagicMock()

    consulta_fotos.filter.return_value.subquery.return_value = subquery

    esperado = [(pessoa, uuid4())]
    consulta_pessoas.outerjoin.return_value.all.return_value = esperado

    db.query.side_effect = [
        consulta_fotos,
        consulta_pessoas,
    ]

    resultado = repository.listar()

    assert db.query.call_count == 2
    consulta_fotos.filter.assert_called_once()
    consulta_fotos.filter.return_value.subquery.assert_called_once()
    consulta_pessoas.outerjoin.assert_called_once()
    assert resultado == esperado


def test_listar_pessoas_sem_resultados(repository, db):
    consulta_fotos = MagicMock()
    consulta_pessoas = MagicMock()

    subquery = MagicMock()
    subquery.c.foto_id = MagicMock()
    subquery.c.pessoa_id = MagicMock()
    subquery.c.numero = MagicMock()

    consulta_fotos.filter.return_value.subquery.return_value = subquery
    consulta_pessoas.outerjoin.return_value.all.return_value = []

    db.query.side_effect = [
        consulta_fotos,
        consulta_pessoas,
    ]

    resultado = repository.listar()

    assert resultado == []


def test_atualizar_pessoa(repository, db, pessoa):
    resultado = repository.atualizar(pessoa)

    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(pessoa)

    assert resultado is pessoa


def test_atualizar_pessoa_faz_rollback_em_erro(
    repository,
    db,
    pessoa,
):
    db.commit.side_effect = Exception("Erro ao atualizar")

    with pytest.raises(Exception, match="Erro ao atualizar"):
        repository.atualizar(pessoa)

    db.rollback.assert_called_once()


def test_deletar_pessoa(repository, db, pessoa):
    resultado = repository.deletar(pessoa)

    db.delete.assert_called_once_with(pessoa)
    db.commit.assert_called_once()

    assert resultado is None


def test_deletar_pessoa_faz_rollback_em_erro(
    repository,
    db,
    pessoa,
):
    db.commit.side_effect = Exception("Erro ao excluir")

    with pytest.raises(Exception, match="Erro ao excluir"):
        repository.deletar(pessoa)

    db.delete.assert_called_once_with(pessoa)
    db.rollback.assert_called_once()


# ==========================================================
# TESTES DO SCHEMA - PESSOA CREATE
# ==========================================================

def test_pessoa_create_com_dados_validos():
    dados = PessoaCreate(
        nome="  Maria da Silva  ",
        cpf="12345678901",
        data_nascimento=date(1990, 5, 10),
        sexo="f",
    )

    assert dados.nome == "Maria da Silva"
    assert dados.cpf == "12345678901"
    assert dados.sexo == "F"


def test_pessoa_create_sem_dados_opcionais():
    dados = PessoaCreate(
        nome="Maria da Silva",
    )

    assert dados.cpf is None
    assert dados.data_nascimento is None
    assert dados.sexo is None


@pytest.mark.parametrize(
    "nome",
    [
        "",
        "  ",
        "AB",
        "A" * 151,
    ],
)
def test_pessoa_create_rejeita_nome_invalido(nome):
    with pytest.raises(ValidationError):
        PessoaCreate(nome=nome)


def test_pessoa_create_rejeita_cpf_com_letras():
    with pytest.raises(
        ValidationError,
        match="O CPF deve conter apenas números.",
    ):
        PessoaCreate(
            nome="Maria da Silva",
            cpf="1234567890A",
        )


@pytest.mark.parametrize(
    "cpf",
    [
        "1234567890",
        "123456789012",
    ],
)
def test_pessoa_create_rejeita_cpf_com_tamanho_invalido(cpf):
    with pytest.raises(ValidationError):
        PessoaCreate(
            nome="Maria da Silva",
            cpf=cpf,
        )


@pytest.mark.parametrize(
    "sexo",
    [
        "X",
        "MASCULINO",
        "1",
    ],
)
def test_pessoa_create_rejeita_sexo_invalido(sexo):
    with pytest.raises(ValidationError):
        PessoaCreate(
            nome="Maria da Silva",
            sexo=sexo,
        )


def test_pessoa_create_aceita_sexo_masculino():
    dados = PessoaCreate(
        nome="João da Silva",
        sexo="m",
    )

    assert dados.sexo == "M"


def test_pessoa_create_aceita_sexo_feminino():
    dados = PessoaCreate(
        nome="Maria da Silva",
        sexo="f",
    )

    assert dados.sexo == "F"


def test_pessoa_create_rejeita_data_de_nascimento_futura():
    with pytest.raises(
        ValidationError,
        match="A data de nascimento não pode ser futura.",
    ):
        PessoaCreate(
            nome="Maria da Silva",
            data_nascimento=date.today() + timedelta(days=1),
        )


def test_pessoa_create_aceita_data_de_nascimento_atual():
    dados = PessoaCreate(
        nome="Maria da Silva",
        data_nascimento=date.today(),
    )

    assert dados.data_nascimento == date.today()


def test_pessoa_create_aceita_cpf_nulo():
    dados = PessoaCreate(
        nome="Maria da Silva",
        cpf=None,
    )

    assert dados.cpf is None


def test_pessoa_create_aceita_sexo_nulo():
    dados = PessoaCreate(
        nome="Maria da Silva",
        sexo=None,
    )

    assert dados.sexo is None


# ==========================================================
# TESTES DO SCHEMA - PESSOA UPDATE
# ==========================================================

def test_pessoa_update_com_dados_validos():
    dados = PessoaUpdate(
        nome="  Maria Atualizada  ",
        cpf="12345678901",
        data_nascimento=date(1995, 1, 1),
        sexo="f",
    )

    assert dados.nome == "Maria Atualizada"
    assert dados.cpf == "12345678901"
    assert dados.sexo == "F"


def test_pessoa_update_sem_campos():
    dados = PessoaUpdate()

    assert dados.nome is None
    assert dados.cpf is None
    assert dados.data_nascimento is None
    assert dados.sexo is None


def test_pessoa_update_rejeita_cpf_com_letras():
    with pytest.raises(
        ValidationError,
        match="O CPF deve conter apenas números.",
    ):
        PessoaUpdate(cpf="1234567890A")


@pytest.mark.parametrize(
    "cpf",
    [
        "1234567890",
        "123456789012",
    ],
)
def test_pessoa_update_rejeita_cpf_com_tamanho_invalido(cpf):
    with pytest.raises(ValidationError):
        PessoaUpdate(cpf=cpf)


@pytest.mark.parametrize(
    "sexo",
    [
        "X",
        "MASCULINO",
        "1",
    ],
)
def test_pessoa_update_rejeita_sexo_invalido(sexo):
    with pytest.raises(ValidationError):
        PessoaUpdate(sexo=sexo)


def test_pessoa_update_aceita_sexo_minusculo():
    dados = PessoaUpdate(sexo="m")

    assert dados.sexo == "M"


def test_pessoa_update_aceita_sexo_nulo():
    dados = PessoaUpdate(sexo=None)

    assert dados.sexo is None


@pytest.mark.parametrize(
    "nome",
    [
        "",
        "  ",
        "AB",
        "A" * 151,
    ],
)
def test_pessoa_update_rejeita_nome_invalido(nome):
    with pytest.raises(ValidationError):
        PessoaUpdate(nome=nome)


def test_pessoa_update_aceita_nome_nulo():
    dados = PessoaUpdate(nome=None)

    assert dados.nome is None


def test_pessoa_update_rejeita_data_futura():
    with pytest.raises(
        ValidationError,
        match="A data de nascimento não pode ser futura.",
    ):
        PessoaUpdate(
            data_nascimento=date.today() + timedelta(days=1),
        )


def test_pessoa_update_aceita_data_nula():
    dados = PessoaUpdate(data_nascimento=None)

    assert dados.data_nascimento is None


# ==========================================================
# TESTES DO SCHEMA - RESPONSE
# ==========================================================

def test_pessoa_response_com_dados_completos(pessoa_id):
    resposta = PessoaResponse(
        id=pessoa_id,
        nome="Maria da Silva",
        cpf="12345678901",
        data_nascimento=date(1990, 5, 10),
        sexo="F",
    )

    assert resposta.id == pessoa_id
    assert resposta.nome == "Maria da Silva"
    assert resposta.cpf == "12345678901"


def test_pessoa_response_com_campos_opcionais_nulos(pessoa_id):
    resposta = PessoaResponse(
        id=pessoa_id,
        nome="Maria da Silva",
    )

    assert resposta.cpf is None
    assert resposta.data_nascimento is None
    assert resposta.sexo is None


def test_pessoa_response_from_attributes(pessoa):
    resposta = PessoaResponse.model_validate(
        pessoa,
        from_attributes=True,
    )

    assert resposta.id == pessoa.id
    assert resposta.nome == pessoa.nome
    assert resposta.cpf == pessoa.cpf


def test_pessoa_lista_response_com_foto(pessoa_id):
    foto_id = uuid4()

    resposta = PessoaListaResponse(
        id=pessoa_id,
        nome="Maria da Silva",
        cpf="12345678901",
        data_nascimento=date(1990, 5, 10),
        sexo="F",
        foto_id=foto_id,
    )

    assert resposta.foto_id == foto_id


def test_pessoa_lista_response_sem_foto(pessoa_id):
    resposta = PessoaListaResponse(
        id=pessoa_id,
        nome="Maria da Silva",
    )

    assert resposta.foto_id is None


def test_pessoa_lista_response_from_attributes():
    objeto = SimpleNamespace(
        id=uuid4(),
        nome="Maria da Silva",
        cpf=None,
        data_nascimento=None,
        sexo=None,
        foto_id=None,
    )

    resposta = PessoaListaResponse.model_validate(
        objeto,
        from_attributes=True,
    )

    assert resposta.id == objeto.id
    assert resposta.nome == objeto.nome
    assert resposta.foto_id is None


# ==========================================================
# TESTES DO SERVICE
# ==========================================================

def test_service_criar_com_cpf_disponivel(
    pessoa,
    dados_criacao,
):
    repository = MagicMock()
    repository.buscar_por_cpf.return_value = None
    repository.salvar.return_value = pessoa

    service = PessoaService(repository)

    resultado = service.criar(dados_criacao)

    repository.buscar_por_cpf.assert_called_once_with(
        dados_criacao.cpf
    )
    repository.salvar.assert_called_once()

    pessoa_salva = repository.salvar.call_args.args[0]

    assert pessoa_salva.nome == dados_criacao.nome
    assert pessoa_salva.cpf == dados_criacao.cpf
    assert resultado is pessoa


def test_service_criar_sem_cpf():
    repository = MagicMock()
    pessoa_salva = MagicMock()
    repository.salvar.return_value = pessoa_salva

    service = PessoaService(repository)

    dados = PessoaCreate(
        nome="Maria da Silva",
    )

    resultado = service.criar(dados)

    repository.buscar_por_cpf.assert_not_called()
    repository.salvar.assert_called_once()

    assert resultado is pessoa_salva


def test_service_criar_com_cpf_duplicado(dados_criacao):
    repository = MagicMock()
    repository.buscar_por_cpf.return_value = MagicMock()

    service = PessoaService(repository)

    with pytest.raises(
        ValueError,
        match="Já existe uma pessoa cadastrada com este CPF.",
    ):
        service.criar(dados_criacao)

    repository.salvar.assert_not_called()


def test_service_cpf_disponivel():
    repository = MagicMock()
    repository.buscar_por_cpf.return_value = None

    service = PessoaService(repository)

    resultado = service.cpf_disponivel("12345678901")

    assert resultado is True


def test_service_cpf_indisponivel():
    repository = MagicMock()
    repository.buscar_por_cpf.return_value = MagicMock()

    service = PessoaService(repository)

    resultado = service.cpf_disponivel("12345678901")

    assert resultado is False


def test_service_listar():
    repository = MagicMock()

    pessoa1 = SimpleNamespace(
        id=uuid4(),
        nome="Maria",
        cpf="12345678901",
        data_nascimento=date(1990, 1, 1),
        sexo="F",
    )
    pessoa2 = SimpleNamespace(
        id=uuid4(),
        nome="João",
        cpf=None,
        data_nascimento=None,
        sexo=None,
    )

    foto_id = uuid4()

    repository.listar.return_value = [
        (pessoa1, foto_id),
        (pessoa2, None),
    ]

    service = PessoaService(repository)

    resultado = service.listar()

    assert len(resultado) == 2
    assert resultado[0]["id"] == pessoa1.id
    assert resultado[0]["foto_id"] == foto_id
    assert resultado[1]["id"] == pessoa2.id
    assert resultado[1]["foto_id"] is None


def test_service_buscar_por_id(pessoa_id, pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa

    service = PessoaService(repository)

    resultado = service.buscar_por_id(pessoa_id)

    repository.buscar_por_id.assert_called_once_with(pessoa_id)
    assert resultado is pessoa


def test_service_atualizar_pessoa_inexistente(pessoa_id):
    repository = MagicMock()
    repository.buscar_por_id.return_value = None

    service = PessoaService(repository)

    with pytest.raises(
        ValueError,
        match="Pessoa não encontrada.",
    ):
        service.atualizar(
            pessoa_id,
            PessoaUpdate(nome="Maria Atualizada"),
        )

    repository.atualizar.assert_not_called()


def test_service_atualizar_nome(pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa
    repository.atualizar.return_value = pessoa

    service = PessoaService(repository)

    dados = PessoaUpdate(nome="Nome Atualizado")

    resultado = service.atualizar(pessoa.id, dados)

    assert pessoa.nome == "Nome Atualizado"
    repository.atualizar.assert_called_once_with(pessoa)
    assert resultado is pessoa


def test_service_atualizar_cpf_sem_duplicidade(pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa
    repository.buscar_por_cpf.return_value = None
    repository.atualizar.return_value = pessoa

    service = PessoaService(repository)

    dados = PessoaUpdate(cpf="98765432100")

    resultado = service.atualizar(pessoa.id, dados)

    repository.buscar_por_cpf.assert_called_once_with("98765432100")
    assert pessoa.cpf == "98765432100"
    assert resultado is pessoa


def test_service_atualizar_mantem_cpf_da_propria_pessoa(pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa
    repository.buscar_por_cpf.return_value = pessoa
    repository.atualizar.return_value = pessoa

    service = PessoaService(repository)

    dados = PessoaUpdate(cpf=pessoa.cpf)

    resultado = service.atualizar(pessoa.id, dados)

    assert pessoa.cpf == "12345678901"
    repository.atualizar.assert_called_once_with(pessoa)
    assert resultado is pessoa


def test_service_atualizar_cpf_pertencente_a_outra_pessoa(pessoa):
    repository = MagicMock()
    outra_pessoa = SimpleNamespace(
        id=uuid4(),
        cpf="98765432100",
    )

    repository.buscar_por_id.return_value = pessoa
    repository.buscar_por_cpf.return_value = outra_pessoa

    service = PessoaService(repository)

    with pytest.raises(
        ValueError,
        match="Já existe uma pessoa cadastrada com este CPF.",
    ):
        service.atualizar(
            pessoa.id,
            PessoaUpdate(cpf="98765432100"),
        )

    repository.atualizar.assert_not_called()


def test_service_atualizar_data_nascimento_e_sexo(pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa
    repository.atualizar.return_value = pessoa

    service = PessoaService(repository)

    nova_data = date(1995, 4, 20)
    dados = PessoaUpdate(
        data_nascimento=nova_data,
        sexo="F",
    )

    resultado = service.atualizar(pessoa.id, dados)

    assert pessoa.data_nascimento == nova_data
    assert pessoa.sexo == "F"
    assert resultado is pessoa


def test_service_deletar_pessoa_inexistente(pessoa_id):
    repository = MagicMock()
    repository.buscar_por_id.return_value = None

    service = PessoaService(repository)

    with pytest.raises(
        ValueError,
        match="Pessoa não encontrada.",
    ):
        service.deletar(pessoa_id)

    repository.deletar.assert_not_called()


def test_service_deletar_pessoa(pessoa):
    repository = MagicMock()
    repository.buscar_por_id.return_value = pessoa

    service = PessoaService(repository)

    resultado = service.deletar(pessoa.id)

    repository.deletar.assert_called_once_with(pessoa)
    assert resultado is None


# ==========================================================
# TESTES DO ROUTER
# ==========================================================

def test_criar_pessoa_sucesso(
    db,
    agente_atual,
    dados_criacao,
    pessoa,
):
    with patch.object(router, "PessoaRepository") as repo_class, \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.criar.return_value = pessoa

        resultado = router.criar_pessoa(
            dados_criacao,
            db,
            agente_atual,
        )

        repo_class.assert_called_once_with(db)
        service_class.assert_called_once_with(repo_class.return_value)
        service_class.return_value.criar.assert_called_once_with(
            dados_criacao
        )

    assert resultado is pessoa


def test_criar_pessoa_com_conflito(
    db,
    agente_atual,
    dados_criacao,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.criar.side_effect = ValueError(
            "Já existe uma pessoa cadastrada com este CPF."
        )

        with pytest.raises(HTTPException) as erro:
            router.criar_pessoa(
                dados_criacao,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 409
    assert erro.value.detail == (
        "Já existe uma pessoa cadastrada com este CPF."
    )


def test_verificar_cpf_disponivel(db, agente_atual):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.cpf_disponivel.return_value = True

        resultado = router.verificar_cpf(
            "12345678901",
            db,
            agente_atual,
        )

    assert resultado == {"disponivel": True}


def test_verificar_cpf_indisponivel(db, agente_atual):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.cpf_disponivel.return_value = False

        resultado = router.verificar_cpf(
            "12345678901",
            db,
            agente_atual,
        )

    assert resultado == {"disponivel": False}


def test_listar_pessoas(db, agente_atual):
    esperado = [{"id": uuid4(), "nome": "Maria"}]

    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.listar.return_value = esperado

        resultado = router.listar_pessoas(db, agente_atual)

    assert resultado == esperado


def test_buscar_pessoa_sucesso(db, agente_atual, pessoa_id, pessoa):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.buscar_por_id.return_value = pessoa

        resultado = router.buscar_pessoa(
            pessoa_id,
            db,
            agente_atual,
        )

    assert resultado is pessoa


def test_buscar_pessoa_nao_encontrada(
    db,
    agente_atual,
    pessoa_id,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.buscar_por_id.return_value = None

        with pytest.raises(HTTPException) as erro:
            router.buscar_pessoa(
                pessoa_id,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == "Pessoa não encontrada."


def test_atualizar_pessoa_sucesso(
    db,
    agente_atual,
    pessoa_id,
    pessoa,
    dados_atualizacao,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.atualizar.return_value = pessoa

        resultado = router.atualizar_pessoa(
            pessoa_id,
            dados_atualizacao,
            db,
            agente_atual,
        )

    assert resultado is pessoa


def test_atualizar_pessoa_nao_encontrada(
    db,
    agente_atual,
    pessoa_id,
    dados_atualizacao,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.atualizar.side_effect = ValueError(
            "Pessoa não encontrada."
        )

        with pytest.raises(HTTPException) as erro:
            router.atualizar_pessoa(
                pessoa_id,
                dados_atualizacao,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == "Pessoa não encontrada."


def test_atualizar_pessoa_com_cpf_duplicado(
    db,
    agente_atual,
    pessoa_id,
    dados_atualizacao,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.atualizar.side_effect = ValueError(
            "Já existe uma pessoa cadastrada com este CPF."
        )

        with pytest.raises(HTTPException) as erro:
            router.atualizar_pessoa(
                pessoa_id,
                dados_atualizacao,
                db,
                agente_atual,
            )

    assert erro.value.status_code == 409
    assert erro.value.detail == (
        "Já existe uma pessoa cadastrada com este CPF."
    )


def test_deletar_pessoa_sucesso(
    db,
    admin_atual,
    pessoa_id,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        resultado = router.deletar_pessoa(
            pessoa_id,
            db,
            admin_atual,
        )

    service_class.return_value.deletar.assert_called_once_with(pessoa_id)
    assert resultado is None


def test_deletar_pessoa_nao_encontrada(
    db,
    admin_atual,
    pessoa_id,
):
    with patch.object(router, "PessoaRepository"), \
         patch.object(router, "PessoaService") as service_class:

        service_class.return_value.deletar.side_effect = ValueError(
            "Pessoa não encontrada."
        )

        with pytest.raises(HTTPException) as erro:
            router.deletar_pessoa(
                pessoa_id,
                db,
                admin_atual,
            )

    assert erro.value.status_code == 404
    assert erro.value.detail == "Pessoa não encontrada."