from uuid import uuid4

import pytest

from app.enderecos.model import Endereco
from app.enderecos.repository import EnderecoRepository
from app.enderecos.schema import EnderecoCreate, EnderecoUpdate
from app.enderecos.service import EnderecoService
from app.pessoas.model import Pessoa


def criar_pessoa(db):
    pessoa = Pessoa(
        nome="João da Silva",
        cpf=str(uuid4())[:11],
        data_nascimento="1990-01-01",
        sexo="M",
        nome_mae="Maria da Silva",
        nome_pai="José da Silva"
    )

    db.add(pessoa)
    db.commit()
    db.refresh(pessoa)

    return pessoa


def criar_endereco(db, pessoa_id):
    endereco = Endereco(
        pessoa_id=pessoa_id,
        logradouro="Rua das Flores",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        cep="01001000"
    )

    db.add(endereco)
    db.commit()
    db.refresh(endereco)

    return endereco


def criar_service(db):
    return EnderecoService(
        EnderecoRepository(db)
    )


def test_criar_endereco(db):
    pessoa = criar_pessoa(db)
    service = criar_service(db)

    dados = EnderecoCreate(
        pessoa_id=pessoa.id,
        logradouro="Rua das Flores",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        cep="01001000"
    )

    endereco = service.criar(dados)

    assert endereco.id is not None
    assert endereco.pessoa_id == pessoa.id
    assert endereco.logradouro == "Rua das Flores"


def test_criar_endereco_pessoa_inexistente(db):
    service = criar_service(db)

    dados = EnderecoCreate(
        pessoa_id=uuid4(),
        logradouro="Rua das Flores",
        numero="123",
        bairro="Centro",
        cidade="São Paulo",
        estado="SP",
        cep="01001000"
    )

    with pytest.raises(ValueError, match="Pessoa não encontrada."):
        service.criar(dados)


def test_listar_enderecos(db):
    pessoa = criar_pessoa(db)

    criar_endereco(db, pessoa.id)
    criar_endereco(db, pessoa.id)

    service = criar_service(db)

    enderecos = service.listar()

    assert len(enderecos) == 2


def test_buscar_endereco(db):
    pessoa = criar_pessoa(db)
    endereco = criar_endereco(db, pessoa.id)

    service = criar_service(db)

    resultado = service.buscar_por_id(endereco.id)

    assert resultado.id == endereco.id


def test_buscar_endereco_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Endereço não encontrado."):
        service.buscar_por_id(uuid4())


def test_listar_enderecos_por_pessoa(db):
    pessoa = criar_pessoa(db)

    criar_endereco(db, pessoa.id)
    criar_endereco(db, pessoa.id)

    service = criar_service(db)

    enderecos = service.listar_por_pessoa(pessoa.id)

    assert len(enderecos) == 2
    assert all(e.pessoa_id == pessoa.id for e in enderecos)


def test_listar_enderecos_pessoa_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Pessoa não encontrada."):
        service.listar_por_pessoa(uuid4())


def test_atualizar_endereco(db):
    pessoa = criar_pessoa(db)
    endereco = criar_endereco(db, pessoa.id)

    service = criar_service(db)

    dados = EnderecoUpdate(
        logradouro="Avenida Paulista",
        numero="1000"
    )

    resultado = service.atualizar(endereco.id, dados)

    assert resultado.logradouro == "Avenida Paulista"
    assert resultado.numero == "1000"

    # Campos não informados permanecem iguais
    assert resultado.bairro == "Centro"
    assert resultado.cidade == "São Paulo"


def test_atualizar_endereco_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Endereço não encontrado."):
        service.atualizar(
            uuid4(),
            EnderecoUpdate(logradouro="Rua Nova")
        )


def test_deletar_endereco(db):
    pessoa = criar_pessoa(db)
    endereco = criar_endereco(db, pessoa.id)

    service = criar_service(db)

    service.deletar(endereco.id)

    assert service.repository.buscar_por_id(endereco.id) is None


def test_deletar_endereco_inexistente(db):
    service = criar_service(db)

    with pytest.raises(ValueError, match="Endereço não encontrado."):
        service.deletar(uuid4())