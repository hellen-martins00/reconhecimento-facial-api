from uuid import uuid4

from app.agentes.model import Agente
from app.auth.service import pwd_context


# ==========================================================
# FUNÇÃO AUXILIAR - LOGIN DE AGENTE
# ==========================================================

def login_agente(client, db):

    senha = "123456"

    agente = Agente(
        nome="Agente Telefone Teste",
        usuario=f"agente_telefone_{uuid4()}",
        senha_hash=pwd_context.hash(senha),
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    response = client.post(
        "/login",
        json={
            "usuario": agente.usuario,
            "senha": senha
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return token


# ==========================================================
# FUNÇÃO AUXILIAR - LOGIN DE ADMIN
# ==========================================================

def login_admin(client, db):

    senha = "123456"

    admin = Agente(
        nome="Administrador Telefone Teste",
        usuario=f"admin_telefone_{uuid4()}",
        senha_hash=pwd_context.hash(senha),
        perfil="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    response = client.post(
        "/login",
        json={
            "usuario": admin.usuario,
            "senha": senha
        }
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return token


# ==========================================================
# CRIAR TELEFONE
# ==========================================================

def test_criar_telefone(client, db):

    token = login_admin(client, db)

    # ------------------------------------------------------
    # Primeiro cria uma pessoa
    # ------------------------------------------------------

    pessoa = {
        "nome": "Pessoa Teste Telefone",
        "cpf": str(uuid4())[:11],
        "data_nascimento": "1995-05-10",
        "sexo": "M",
        "nome_mae": "Maria Teste",
        "nome_pai": "Joao Teste"
    }

    response_pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert response_pessoa.status_code == 201

    pessoa_id = response_pessoa.json()["id"]

    # ------------------------------------------------------
    # Agora cria o telefone
    # ------------------------------------------------------

    telefone = {
        "pessoa_id": pessoa_id,
        "numero": "61999999999",
        "tipo": "celular"
    }

    response = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=telefone
    )

    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["pessoa_id"] == pessoa_id
    assert dados["numero"] == "61999999999"
    assert dados["tipo"] == "celular"


# ==========================================================
# CRIAR TELEFONE - PESSOA INEXISTENTE
# ==========================================================

def test_criar_telefone_pessoa_inexistente(client, db):

    token = login_agente(client, db)

    telefone = {
        "pessoa_id": str(uuid4()),
        "numero": "61999999999",
        "tipo": "celular"
    }

    response = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=telefone
    )

    assert response.status_code == 400

    assert response.json()["detail"] == "Pessoa não encontrada."


# ==========================================================
# LISTAR TELEFONES
# ==========================================================

def test_listar_telefones(client, db):

    token = login_agente(client, db)

    response = client.get(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert isinstance(dados, list)


# ==========================================================
# BUSCAR TELEFONE POR ID
# ==========================================================

def test_buscar_telefone(client, db):

    token_admin = login_admin(client, db)

    # ------------------------------------------------------
    # Cria pessoa
    # ------------------------------------------------------

    pessoa = {
        "nome": "Pessoa Busca Telefone",
        "cpf": str(uuid4())[:11],
        "data_nascimento": "1990-01-01",
        "sexo": "M",
        "nome_mae": "Maria Teste",
        "nome_pai": "Joao Teste"
    }

    response_pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token_admin}"
        },
        json=pessoa
    )

    assert response_pessoa.status_code == 201

    pessoa_id = response_pessoa.json()["id"]

    # ------------------------------------------------------
    # Cria telefone
    # ------------------------------------------------------

    telefone = {
        "pessoa_id": pessoa_id,
        "numero": "61988888888",
        "tipo": "celular"
    }

    response_telefone = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token_admin}"
        },
        json=telefone
    )

    assert response_telefone.status_code == 201

    telefone_id = response_telefone.json()["id"]

    # ------------------------------------------------------
    # Busca
    # ------------------------------------------------------

    response = client.get(
        f"/telefones/{telefone_id}",
        headers={
            "Authorization": f"Bearer {token_admin}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["id"] == telefone_id
    assert dados["pessoa_id"] == pessoa_id
    assert dados["numero"] == "61988888888"
    assert dados["tipo"] == "celular"


# ==========================================================
# BUSCAR TELEFONE INEXISTENTE
# ==========================================================

def test_buscar_telefone_inexistente(client, db):

    token = login_agente(client, db)

    id_inexistente = str(uuid4())

    response = client.get(
        f"/telefones/{id_inexistente}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Telefone não encontrado."


# ==========================================================
# LISTAR TELEFONES POR PESSOA
# ==========================================================

def test_listar_telefones_por_pessoa(client, db):

    token = login_admin(client, db)

    # ------------------------------------------------------
    # Cria pessoa
    # ------------------------------------------------------

    pessoa = {
        "nome": "Pessoa Lista Telefones",
        "cpf": str(uuid4())[:11],
        "data_nascimento": "1992-02-02",
        "sexo": "F",
        "nome_mae": "Maria Teste",
        "nome_pai": "Joao Teste"
    }

    response_pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert response_pessoa.status_code == 201

    pessoa_id = response_pessoa.json()["id"]

    # ------------------------------------------------------
    # Cria telefone
    # ------------------------------------------------------

    telefone = {
        "pessoa_id": pessoa_id,
        "numero": "61977777777",
        "tipo": "celular"
    }

    response_telefone = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=telefone
    )

    assert response_telefone.status_code == 201

    # ------------------------------------------------------
    # Lista telefones da pessoa
    # ------------------------------------------------------

    response = client.get(
        f"/telefones/pessoa/{pessoa_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200

    dados = response.json()

    assert isinstance(dados, list)
    assert len(dados) >= 1
    assert dados[0]["pessoa_id"] == pessoa_id


# ==========================================================
# LISTAR TELEFONES - PESSOA INEXISTENTE
# ==========================================================

def test_listar_telefones_pessoa_inexistente(client, db):

    token = login_agente(client, db)

    pessoa_id_inexistente = str(uuid4())

    response = client.get(
        f"/telefones/pessoa/{pessoa_id_inexistente}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Pessoa não encontrada."


# ==========================================================
# ATUALIZAR TELEFONE
# ==========================================================

def test_atualizar_telefone(client, db):

    token = login_admin(client, db)

    # ------------------------------------------------------
    # Cria pessoa
    # ------------------------------------------------------

    pessoa = {
        "nome": "Pessoa Atualizar Telefone",
        "cpf": str(uuid4())[:11],
        "data_nascimento": "1991-03-03",
        "sexo": "M",
        "nome_mae": "Maria Teste",
        "nome_pai": "Joao Teste"
    }

    response_pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert response_pessoa.status_code == 201

    pessoa_id = response_pessoa.json()["id"]

    # ------------------------------------------------------
    # Cria telefone
    # ------------------------------------------------------

    telefone = {
        "pessoa_id": pessoa_id,
        "numero": "61966666666",
        "tipo": "celular"
    }

    response_telefone = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=telefone
    )

    assert response_telefone.status_code == 201

    telefone_id = response_telefone.json()["id"]

    # ------------------------------------------------------
    # Atualiza
    # ------------------------------------------------------

    dados_atualizacao = {
        "numero": "61955555555",
        "tipo": "residencial"
    }

    response = client.put(
        f"/telefones/{telefone_id}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados_atualizacao
    )

    assert response.status_code == 200

    dados = response.json()

    assert dados["id"] == telefone_id
    assert dados["numero"] == "61955555555"
    assert dados["tipo"] == "residencial"


# ==========================================================
# ATUALIZAR TELEFONE INEXISTENTE
# ==========================================================

def test_atualizar_telefone_inexistente(client, db):

    token = login_admin(client, db)

    id_inexistente = str(uuid4())

    dados = {
        "numero": "61944444444",
        "tipo": "celular"
    }

    response = client.put(
        f"/telefones/{id_inexistente}",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Telefone não encontrado."


# ==========================================================
# EXCLUIR TELEFONE
# ==========================================================

def test_deletar_telefone(client, db):

    token = login_admin(client, db)

    # ------------------------------------------------------
    # Cria pessoa
    # ------------------------------------------------------

    pessoa = {
        "nome": "Pessoa Deletar Telefone",
        "cpf": str(uuid4())[:11],
        "data_nascimento": "1993-04-04",
        "sexo": "M",
        "nome_mae": "Maria Teste",
        "nome_pai": "Joao Teste"
    }

    response_pessoa = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=pessoa
    )

    assert response_pessoa.status_code == 201

    pessoa_id = response_pessoa.json()["id"]

    # ------------------------------------------------------
    # Cria telefone
    # ------------------------------------------------------

    telefone = {
        "pessoa_id": pessoa_id,
        "numero": "61933333333",
        "tipo": "celular"
    }

    response_telefone = client.post(
        "/telefones",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=telefone
    )

    assert response_telefone.status_code == 201

    telefone_id = response_telefone.json()["id"]

    # ------------------------------------------------------
    # Deleta
    # ------------------------------------------------------

    response = client.delete(
        f"/telefones/{telefone_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 204


# ==========================================================
# DELETAR TELEFONE INEXISTENTE
# ==========================================================

def test_deletar_telefone_inexistente(client, db):

    token = login_admin(client, db)

    id_inexistente = str(uuid4())

    response = client.delete(
        f"/telefones/{id_inexistente}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Telefone não encontrado."