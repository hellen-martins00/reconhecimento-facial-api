from app.agentes.model import Agente
from app.auth.service import pwd_context


def test_login_sucesso(client, db):

    senha = "123456"

    senha_hash = pwd_context.hash(senha)

    agente = Agente(
        nome="Agente Teste",
        usuario="agente_teste",
        senha_hash=senha_hash,
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    try:

        response = client.post(
            "/login",
            json={
                "usuario": "agente_teste",
                "senha": senha
            }
        )

        assert response.status_code == 200

        dados = response.json()

        assert "access_token" in dados
        assert dados["token_type"] == "bearer"
        assert dados["usuario"] == "agente_teste"
        assert dados["nome"] == "Agente Teste"

    finally:

        db.delete(agente)
        db.commit()
        
        
def test_login_senha_incorreta(client, db):
    senha = "123456"

    senha_hash = pwd_context.hash(senha)

    agente = Agente(
        nome="Agente Teste",
        usuario="agente_teste",
        senha_hash=senha_hash,
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    response = client.post(
        "/login",
        json={
            "usuario": "agente_teste",
            "senha": "senha_errada"
        }
    )

    assert response.status_code == 401

    dados = response.json()

    assert dados["detail"] == "Usuário ou senha inválidos."
    
def test_login_usuario_inexistente(client):
    response = client.post(
        "/login",
        json={
            "usuario": "usuario_que_nao_existe",
            "senha": "123456"
        }
    )

    assert response.status_code == 401

    dados = response.json()

    assert dados["detail"] == "Usuário ou senha inválidos."

def test_acesso_com_token_valido(client, db):

    senha = "123456"

    senha_hash = pwd_context.hash(senha)

    agente = Agente(
        nome="Agente Teste",
        usuario="agente_teste",
        senha_hash=senha_hash,
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    response_login = client.post(
        "/login",
        json={
            "usuario": "agente_teste",
            "senha": senha
        }
    )

    assert response_login.status_code == 200

    token = response_login.json()["access_token"]

    response = client.get(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    
def test_acesso_sem_token(client):

    response = client.get(
        "/pessoas"
    )

    assert response.status_code == 401 #403
    
def test_acesso_com_token_invalido(client):

    response = client.get(
        "/pessoas",
        headers={
            "Authorization": "Bearer token_invalido"
        }
    )

    assert response.status_code == 401

    dados = response.json()

    assert dados["detail"] == "Token inválido ou expirado."
    
def test_agente_pode_criar_pessoa(client, db):

    senha = "123456"

    agente = Agente(
        nome="Agente Comum",
        usuario="agente_comum_teste_2",
        senha_hash=pwd_context.hash(senha),
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    # Login do agente
    response_login = client.post(
        "/login",
        json={
            "usuario": "agente_comum_teste_2",
            "senha": senha
        }
    )

    assert response_login.status_code == 200

    token = response_login.json()["access_token"]

    # AGENTE cadastra uma pessoa
    response = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "nome": "Pessoa Teste Agente",
            "cpf": "12345678901",
            "data_nascimento": "1990-01-01",
            "sexo": "M",
            "nome_mae": "Maria Teste",
            "nome_pai": "Joao Teste"
        }
    )

    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["nome"] == "Pessoa Teste Agente"
    assert dados["cpf"] == "12345678901"
    assert dados["sexo"] == "M"
    
def test_admin_pode_criar_pessoa(client, db):

    senha = "123456"

    admin = Agente(
        nome="Administrador Teste",
        usuario="admin_teste_2",
        senha_hash=pwd_context.hash(senha),
        perfil="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    # Login do administrador
    response_login = client.post(
        "/login",
        json={
            "usuario": "admin_teste_2",
            "senha": senha
        }
    )

    assert response_login.status_code == 200

    token = response_login.json()["access_token"]

    # ADMIN cadastra uma pessoa
    response = client.post(
        "/pessoas",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json={
            "nome": "Pessoa Teste Admin",
            "cpf": "57953358000",
            "data_nascimento": "1990-05-10",
            "sexo": "M",
            "nome_mae": "Maria Teste",
            "nome_pai": "Joao Teste"
        }
    )

    print("STATUS:", response.status_code)
    print("RESPOSTA:", response.json())
    
    assert response.status_code == 201

    dados = response.json()

    assert dados["nome"] == "Pessoa Teste Admin"
    assert dados["cpf"] == "57953358000"
    assert dados["sexo"] == "M"