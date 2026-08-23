from uuid import uuid4

import pytest

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.telefones.repository import TelefoneRepository
from app.telefones.schema import TelefoneCreate, TelefoneUpdate
from app.telefones.service import TelefoneService


def criar_pessoa(db):
    pessoa = Pessoa(
        nome="Pessoa Teste",
        cpf=str(uuid4())[:11],
        data_nascimento="1990-01-01",
        sexo="M",
        nome_mae="Maria Teste",
        nome_pai="João Teste"
    )

    db.add(pessoa)
    db.commit()
    db.refresh(pessoa)

    return pessoa


def criar_telefone(db, pessoa_id):
    telefone = Telefone(
        pessoa_id=pessoa_id,
        numero="61999999999",
        tipo="celular"
    )

    db.add(telefone)
    db.commit()
    db.refresh(telefone)

    return telefone


def criar_service(db):
    return TelefoneService(
        TelefoneRepository(db)
    )


# CRIAR
def test_criar_telefone(db):
    pessoa = criar_pessoa(db)
    service = criar_service(db)

    dados = TelefoneCreate(
        pessoa_id=pessoa.id,
        numero="61999999999",
        tipo="celular"
    )

    telefone = service.criar(dados)

    assert telefone.id is not None
    assert telefone.pessoa_id == pessoa.id
    assert telefone.numero == "61999999999"
    assert telefone.tipo == "celular"


def test_criar_telefone_pessoa_inexistente(db):
    service = criar_service(db)

    dados = TelefoneCreate(
        pessoa_id=uuid4(),
        numero="61999999999",
        tipo="celular"
    )

    with pytest.raises(ValueError, match="Pessoa não encontrada."):
        service.criar(dados)


# LISTAR
def test_listar_telefones(db):
    pessoa = criar_pessoa(db)

    criar_telefone(db, pessoa.id)
    criar_telefone(db, pessoa.id)

    service = criar_service(db)

    telefones = service.listar()

    assert len(telefones) == 2


# BUSCAR
def test_buscar_telefone(db):
    pessoa = criar_pessoa(db)
    telefone = criar_telefone(db, pessoa.id)

    service = criar_service(db)

    resultado = service.buscar_por_id(telefone.id)

    assert resultado.id == telefone.id
    assert resultado.pessoa_id == pessoa.id
    assert resultado.numero == "61999999999"


def test_buscar_telefone_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Telefone não encontrado."):
        service.buscar_por_id(uuid4())


# LISTAR POR PESSOA
def test_listar_telefones_por_pessoa(db):
    pessoa = criar_pessoa(db)

    criar_telefone(db, pessoa.id)
    criar_telefone(db, pessoa.id)

    service = criar_service(db)

    telefones = service.listar_por_pessoa(pessoa.id)

    assert len(telefones) == 2
    assert all(
        telefone.pessoa_id == pessoa.id
        for telefone in telefones
    )


def test_listar_telefones_pessoa_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Pessoa não encontrada."):
        service.listar_por_pessoa(uuid4())


# ATUALIZAR
def test_atualizar_telefone(db):
    pessoa = criar_pessoa(db)
    telefone = criar_telefone(db, pessoa.id)

    service = criar_service(db)

    dados = TelefoneUpdate(
        numero="61988888888",
        tipo="residencial"
    )

    resultado = service.atualizar(
        telefone.id,
        dados
    )

    assert resultado.numero == "61988888888"
    assert resultado.tipo == "residencial"


def test_atualizar_telefone_parcial(db):
    pessoa = criar_pessoa(db)
    telefone = criar_telefone(db, pessoa.id)

    service = criar_service(db)

    dados = TelefoneUpdate(
        numero="61988888888"
    )

    resultado = service.atualizar(
        telefone.id,
        dados
    )

    assert resultado.numero == "61988888888"
    assert resultado.tipo == "celular"


def test_atualizar_telefone_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Telefone não encontrado."):
        service.atualizar(
            uuid4(),
            TelefoneUpdate(numero="61988888888")
        )


# DELETAR
def test_deletar_telefone(db):
    pessoa = criar_pessoa(db)
    telefone = criar_telefone(db, pessoa.id)

    service = criar_service(db)

    service.deletar(telefone.id)

    assert service.repository.buscar_por_id(telefone.id) is None


def test_deletar_telefone_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Telefone não encontrado."):
        service.deletar(uuid4())