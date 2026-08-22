from app.agentes.model import Agente
from app.auth.service import pwd_context


def criar_admin(db):
    senha = "123456"

    admin = Agente(
        nome="Administrador Teste",
        usuario="admin_pessoa_teste",
        senha_hash=pwd_context.hash(senha),
        perfil="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin, senha


def criar_agente(db):
    senha = "123456"

    agente = Agente(
        nome="Agente Teste",
        usuario="agente_pessoa_teste",
        senha_hash=pwd_context.hash(senha),
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    return agente, senha


def login(client, usuario, senha):

    response = client.post(
        "/login",
        json={
            "usuario": usuario,
            "senha": senha
        }
    )

    assert response.status_code == 200

    return response.json()["access_token"]


def criar_dados_pessoa(cpf="36918458000"):

    return {
        "nome": "João da Silva",
        "cpf": cpf,
        "data_nascimento": "1990-01-01",
        "sexo": "M",
        "nome_mae": "Maria da Silva",
        "nome_pai": "José da Silva"
    }


def test_criar_pessoa_sucesso(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_pessoa()
    )

    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["nome"] == "João da Silva"
    assert dados["cpf"] == "36918458000"
    assert dados["sexo"] == "M"


def test_criar_pessoa_cpf_duplicado(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    pessoa = criar_dados_pessoa("11122233344")

    primeira = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert primeira.status_code == 201

    segunda = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert segunda.status_code == 400

    dados = segunda.json()

    assert dados["detail"] == (
        "Já existe uma pessoa cadastrada com este CPF."
    )


def test_agente_pode_listar_pessoas(client, db):

    admin, senha_admin = criar_admin(db)

    token_admin = login(
        client,
        "admin_pessoa_teste",
        senha_admin
    )

    pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token_admin}"
        },
        json=criar_dados_pessoa("22233344455")
    )

    assert pessoa.status_code == 201

    agente, senha_agente = criar_agente(db)

    token_agente = login(
        client,
        "agente_pessoa_teste",
        senha_agente
    )

    response = client.get(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token_agente}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_agente_pode_buscar_pessoa(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response_criacao = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_pessoa("33344455566")
    )

    assert response_criacao.status_code == 201

    pessoa = response_criacao.json()

    agente, senha_agente = criar_agente(db)

    token_agente = login(
        client,
        "agente_pessoa_teste",
        senha_agente
    )

    response = client.get(
        f"/pessoas/{pessoa['id']}",
        headers={
            "Authorization": f"Bearer {token_agente}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["id"] == pessoa["id"]
    assert dados["nome"] == "João da Silva"


def test_buscar_pessoa_inexistente(client, db):

    agente, senha = criar_agente(db)

    token = login(
        client,
        "agente_pessoa_teste",
        senha
    )

    response = client.get(
        "/pessoas/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    dados = response.json()

    assert dados["detail"] == "Pessoa não encontrada."


def test_admin_pode_atualizar_pessoa(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response_criacao = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_pessoa("44455566677")
    )

    assert response_criacao.status_code == 201

    pessoa = response_criacao.json()

    response = client.put(
        f"/pessoas/{pessoa['id']}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "nome": "João da Silva Atualizado"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["id"] == pessoa["id"]
    assert dados["nome"] == "João da Silva Atualizado"


def test_admin_nao_pode_atualizar_pessoa_inexistente(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response = client.put(
        "/pessoas/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "nome": "Pessoa Atualizada"
        }
    )

    assert response.status_code == 400

    dados = response.json()

    assert dados["detail"] == "Pessoa não encontrada."


def test_admin_pode_deletar_pessoa(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response_criacao = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_pessoa("55566677788")
    )

    assert response_criacao.status_code == 201

    pessoa = response_criacao.json()

    response = client.delete(
        f"/pessoas/{pessoa['id']}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 204


def test_admin_nao_pode_deletar_pessoa_inexistente(client, db):

    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_pessoa_teste",
        senha
    )

    response = client.delete(
        "/pessoas/00000000-0000-0000-0000-000000000000",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    dados = response.json()

    assert dados["detail"] == "Pessoa não encontrada."