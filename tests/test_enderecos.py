# test_enderecos.py

from app.agentes.model import Agente
from app.auth.service import pwd_context


def criar_admin(db):
    """Cria um administrador para os testes"""
    senha = "123456"

    admin = Agente(
        nome="Administrador Endereco Teste",
        usuario="admin_endereco_teste",
        senha_hash=pwd_context.hash(senha),
        perfil="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin, senha


def criar_agente(db):
    """Cria um agente para os testes"""
    senha = "123456"

    agente = Agente(
        nome="Agente Endereco Teste",
        usuario="agente_endereco_teste",
        senha_hash=pwd_context.hash(senha),
        perfil="AGENTE"
    )

    db.add(agente)
    db.commit()
    db.refresh(agente)

    return agente, senha


def login(client, usuario, senha):
    """Função auxiliar para fazer login"""
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
    """Cria dados de uma pessoa para associar ao endereço"""
    return {
        "nome": "João da Silva",
        "cpf": cpf,
        "data_nascimento": "1990-01-01",
        "sexo": "M",
        "nome_mae": "Maria da Silva",
        "nome_pai": "José da Silva"
    }


def criar_dados_endereco():
    """Cria dados de um endereço para os testes"""
    return {
        "logradouro": "Rua das Flores",
        "numero": "123",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01001000"
    }


def criar_pessoa_para_teste(client, token):
    """Cria uma pessoa para associar aos endereços"""
    response = client.post(
        "/pessoas",
        headers={"Authorization": f"Bearer {token}"},
        json=criar_dados_pessoa()
    )
    assert response.status_code == 201
    return response.json()


# ==================== TESTES DE ENDEREÇOS ====================

def test_criar_endereco_sucesso(client, db):
    """
    Teste: Criar um endereço com sucesso
    Cenário: Admin cria uma pessoa e depois um endereço para ela
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar uma pessoa para associar o endereço
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar o endereço
    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )

    # 4. Verificações
    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["pessoa_id"] == pessoa["id"]
    assert dados["logradouro"] == "Rua das Flores"
    assert dados["numero"] == "123"
    assert dados["bairro"] == "Centro"
    assert dados["cidade"] == "São Paulo"
    assert dados["estado"] == "SP"
    assert dados["cep"] == "01001000"


def test_criar_endereco_pessoa_inexistente(client, db):
    """
    Teste: Criar endereço para pessoa que não existe
    Cenário: Tentar criar um endereço com um pessoa_id inválido
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Tentar criar endereço com pessoa_id inexistente
    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )

    # 3. Verificações
    assert response.status_code == 400
    dados = response.json()
    assert dados["detail"] == "Pessoa não encontrada."


def test_criar_endereco_agente(client, db):
    """
    Teste: Agente pode criar um endereço
    Cenário: Agente cria uma pessoa e um endereço para ela
    """
    # 1. Criar admin para criar a pessoa
    admin, senha_admin = criar_admin(db)
    token_admin = login(client, "admin_endereco_teste", senha_admin)

    # 2. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)
    token_agente = login(client, "agente_endereco_teste", senha_agente)

    # 3. Criar pessoa (com admin)
    pessoa = criar_pessoa_para_teste(client, token_admin)

    # 4. Agente cria endereço
    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token_agente}"},
        json=endereco_data
    )

    # 5. Verificações
    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["pessoa_id"] == pessoa["id"]


def test_listar_enderecos(client, db):
    """
    Teste: Listar todos os endereços
    Cenário: Criar alguns endereços e listar
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar dois endereços para a pessoa
    for i in range(2):
        endereco_data = criar_dados_endereco()
        endereco_data["pessoa_id"] = pessoa["id"]
        endereco_data["numero"] = str(100 + i)

        response = client.post(
            "/enderecos",
            headers={"Authorization": f"Bearer {token}"},
            json=endereco_data
        )
        assert response.status_code == 201

    # 4. Listar endereços
    response = client.get(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) >= 2


def test_buscar_endereco_por_id(client, db):
    """
    Teste: Buscar um endereço específico pelo ID
    Cenário: Criar um endereço e depois buscá-lo
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar endereço
    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )
    assert response_criacao.status_code == 201

    endereco_criado = response_criacao.json()

    # 4. Buscar o endereço pelo ID
    response = client.get(
        f"/enderecos/{endereco_criado['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == endereco_criado["id"]
    assert dados["logradouro"] == "Rua das Flores"


def test_buscar_endereco_inexistente(client, db):
    """
    Teste: Buscar um endereço que não existe
    Cenário: Tentar buscar um endereço com ID inválido
    """
    # 1. Criar agente e fazer login
    agente, senha = criar_agente(db)
    token = login(client, "agente_endereco_teste", senha)

    # 2. Tentar buscar endereço inexistente
    response = client.get(
        "/enderecos/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Endereço não encontrado."


def test_listar_enderecos_por_pessoa(client, db):
    """
    Teste: Listar todos os endereços de uma pessoa específica
    Cenário: Criar uma pessoa com vários endereços e listar
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar 3 endereços para a pessoa
    enderecos_criados = []
    for i in range(3):
        endereco_data = criar_dados_endereco()
        endereco_data["pessoa_id"] = pessoa["id"]
        endereco_data["numero"] = str(100 + i)

        response = client.post(
            "/enderecos",
            headers={"Authorization": f"Bearer {token}"},
            json=endereco_data
        )
        assert response.status_code == 201
        enderecos_criados.append(response.json())

    # 4. Listar endereços da pessoa
    response = client.get(
        f"/enderecos/pessoa/{pessoa['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) == 3

    # Verificar se todos os endereços são da pessoa
    for endereco in dados:
        assert endereco["pessoa_id"] == pessoa["id"]


def test_listar_enderecos_por_pessoa_inexistente(client, db):
    """
    Teste: Listar endereços de uma pessoa que não existe
    Cenário: Tentar listar endereços com pessoa_id inválido
    """
    # 1. Criar agente e fazer login
    agente, senha = criar_agente(db)
    token = login(client, "agente_endereco_teste", senha)

    # 2. Tentar listar endereços de pessoa inexistente
    response = client.get(
        "/enderecos/pessoa/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Pessoa não encontrada."


def test_atualizar_endereco_sucesso(client, db):
    """
    Teste: Atualizar um endereço com sucesso
    Cenário: Admin atualiza os dados de um endereço
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa e endereço
    pessoa = criar_pessoa_para_teste(client, token)

    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )
    assert response_criacao.status_code == 201
    endereco = response_criacao.json()

    # 3. Atualizar endereço
    dados_atualizacao = {
        "logradouro": "Avenida Paulista",
        "numero": "1000",
        "bairro": "Bela Vista",
        "cidade": "São Paulo",
        "estado": "SP",
        "cep": "01311000"
    }

    response = client.put(
        f"/enderecos/{endereco['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_atualizacao
    )

    # 4. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == endereco["id"]
    assert dados["logradouro"] == "Avenida Paulista"
    assert dados["numero"] == "1000"
    assert dados["bairro"] == "Bela Vista"
    assert dados["cep"] == "01311000"


def test_atualizar_endereco_parcial(client, db):
    """
    Teste: Atualizar apenas alguns campos do endereço
    Cenário: Admin atualiza apenas o logradouro e número
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa e endereço
    pessoa = criar_pessoa_para_teste(client, token)

    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )
    assert response_criacao.status_code == 201
    endereco = response_criacao.json()

    # 3. Atualizar apenas alguns campos
    dados_atualizacao = {
        "logradouro": "Rua Nova",
        "numero": "456"
    }

    response = client.put(
        f"/enderecos/{endereco['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json=dados_atualizacao
    )

    # 4. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert dados["logradouro"] == "Rua Nova"
    assert dados["numero"] == "456"
    # Os outros campos devem permanecer iguais
    assert dados["bairro"] == "Centro"
    assert dados["cidade"] == "São Paulo"


def test_atualizar_endereco_inexistente(client, db):
    """
    Teste: Atualizar um endereço que não existe
    Cenário: Tentar atualizar com ID inválido
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Tentar atualizar endereço inexistente
    response = client.put(
        "/enderecos/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "logradouro": "Rua Nova"
        }
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Endereço não encontrado."


def test_deletar_endereco_sucesso(client, db):
    """
    Teste: Deletar um endereço com sucesso
    Cenário: Admin deleta um endereço existente
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Criar pessoa e endereço
    pessoa = criar_pessoa_para_teste(client, token)

    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token}"},
        json=endereco_data
    )
    assert response_criacao.status_code == 201
    endereco = response_criacao.json()

    # 3. Deletar endereço
    response = client.delete(
        f"/enderecos/{endereco['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Verificações
    assert response.status_code == 204

    # 5. Verificar se o endereço realmente foi deletado
    response_busca = client.get(
        f"/enderecos/{endereco['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_busca.status_code == 404


def test_deletar_endereco_inexistente(client, db):
    """
    Teste: Deletar um endereço que não existe
    Cenário: Tentar deletar com ID inválido
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_endereco_teste", senha)

    # 2. Tentar deletar endereço inexistente
    response = client.delete(
        "/enderecos/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Endereço não encontrado."


def test_agente_pode_atualizar_endereco(client, db):
    """
    Teste: Agente pode atualizar endereço
    Cenário: Agente autenticado altera um endereço.
    """

    # 1. Criar admin e fazer login
    admin, senha_admin = criar_admin(db)

    token_admin = login(
        client,
        "admin_endereco_teste",
        senha_admin
    )

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(
        client,
        token_admin
    )

    # 3. Criar endereço
    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={
            "Authorization": f"Bearer {token_admin}"
        },
        json=endereco_data
    )

    assert response_criacao.status_code == 201

    endereco = response_criacao.json()

    # 4. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)

    token_agente = login(
        client,
        "agente_endereco_teste",
        senha_agente
    )

    # 5. Atualizar endereço como agente
    response = client.put(
        f"/enderecos/{endereco['id']}",
        headers={
            "Authorization": f"Bearer {token_agente}"
        },
        json={
            "logradouro": "Rua Atualizada"
        }
    )

    # 6. Agente pode atualizar
    assert response.status_code == 200

    dados = response.json()

    assert dados["logradouro"] == "Rua Atualizada"


def test_agente_nao_pode_deletar_endereco(client, db):
    """
    Teste: Agente não pode deletar endereço (apenas admin)
    Cenário: Agente tenta deletar um endereço e é bloqueado
    """
    # 1. Criar admin e fazer login
    admin, senha_admin = criar_admin(db)
    token_admin = login(client, "admin_endereco_teste", senha_admin)

    # 2. Criar pessoa e endereço (com admin)
    pessoa = criar_pessoa_para_teste(client, token_admin)

    endereco_data = criar_dados_endereco()
    endereco_data["pessoa_id"] = pessoa["id"]

    response_criacao = client.post(
        "/enderecos",
        headers={"Authorization": f"Bearer {token_admin}"},
        json=endereco_data
    )
    assert response_criacao.status_code == 201
    endereco = response_criacao.json()

    # 3. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)
    token_agente = login(client, "agente_endereco_teste", senha_agente)

    # 4. Tentar deletar endereço como agente
    response = client.delete(
        f"/enderecos/{endereco['id']}",
        headers={"Authorization": f"Bearer {token_agente}"}
    )

    # 5. Verificações - Deve retornar 403 ou 401 (acesso negado)
    assert response.status_code in [401, 403]
