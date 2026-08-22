# test_passagens.py

from app.agentes.model import Agente
from app.auth.service import pwd_context


def criar_admin(db):
    """Cria um administrador para os testes"""
    senha = "123456"

    admin = Agente(
        nome="Administrador Passagem Teste",
        usuario="admin_passagem_teste",
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
        nome="Agente Passagem Teste",
        usuario="agente_passagem_teste",
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
    """Cria dados de uma pessoa para associar à passagem criminal"""
    return {
        "nome": "João da Silva",
        "cpf": cpf,
        "data_nascimento": "1990-01-01",
        "sexo": "M",
        "nome_mae": "Maria da Silva",
        "nome_pai": "José da Silva"
    }


def criar_dados_passagem():
    """Cria dados de uma passagem criminal para os testes"""
    return {
        "crime": "Roubo",
        "descricao": "Roubo a mão armada no centro da cidade",
        "data_ocorrencia": "2024-01-15",
        "delegacia": "1ª Delegacia de Polícia"
    }


def criar_pessoa_para_teste(client, token):
    """Cria uma pessoa para associar às passagens criminais"""
    response = client.post(
        "/pessoas",
        headers={"Authorization": f"Bearer {token}"},
        json=criar_dados_pessoa()
    )
    assert response.status_code == 201
    return response.json()


# ==================== TESTES DE PASSAGENS CRIMINAIS ====================

def test_criar_passagem_sucesso(client, db):
    """
    Teste: Criar uma passagem criminal com sucesso
    Cenário: Admin cria uma pessoa e depois uma passagem criminal para ela
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar uma pessoa para associar a passagem
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar a passagem criminal
    passagem_data = criar_dados_passagem()

    response = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Verificações
    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["pessoa_id"] == pessoa["id"]
    assert dados["crime"] == "Roubo"
    assert dados["descricao"] == "Roubo a mão armada no centro da cidade"
    assert dados["data_ocorrencia"] == "2024-01-15"
    assert dados["delegacia"] == "1ª Delegacia de Polícia"


def test_criar_passagem_pessoa_inexistente(client, db):
    """
    Teste: Criar passagem para pessoa que não existe
    Cenário: Tentar criar uma passagem com um pessoa_id inválido
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Tentar criar passagem com pessoa_id inexistente
    passagem_data = criar_dados_passagem()
    pessoa_id_invalido = "00000000-0000-0000-0000-000000000000"

    response = client.post(
        f"/passagens?pessoa_id={pessoa_id_invalido}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 400
    dados = response.json()
    assert dados["detail"] == "Pessoa não encontrada."


def test_criar_passagem_agente_pode(client, db):
    """
    Teste: Agente pode criar passagem criminal
    Cenário: Agente autenticado cria uma passagem criminal.
    """

    # 1. Criar admin para criar a pessoa
    admin, senha_admin = criar_admin(db)

    token_admin = login(
        client,
        "admin_passagem_teste",
        senha_admin
    )

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(
        client,
        token_admin
    )

    # 3. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)

    token_agente = login(
        client,
        "agente_passagem_teste",
        senha_agente
    )

    # 4. Dados da passagem
    passagem_data = criar_dados_passagem()

    response = client.post(
        (
            f"/passagens?"
            f"pessoa_id={pessoa['id']}"
            f"&crime={passagem_data['crime']}"
            f"&descricao={passagem_data['descricao']}"
            f"&data_ocorrencia={passagem_data['data_ocorrencia']}"
            f"&delegacia={passagem_data['delegacia']}"
        ),
        headers={
            "Authorization": f"Bearer {token_agente}"
        }
    )

    # 5. Agente pode criar
    assert response.status_code == 201

    dados = response.json()

    assert dados["pessoa_id"] == pessoa["id"]
    assert dados["crime"] == passagem_data["crime"]

def test_listar_passagens(client, db):
    """
    Teste: Listar todas as passagens criminais
    Cenário: Criar algumas passagens e listar
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar duas passagens para a pessoa
    passagem_data = criar_dados_passagem()
    for i in range(2):
        crime = f"Crime {i+1}"
        descricao = f"Descrição do crime {i+1}"

        response = client.post(
            f"/passagens?pessoa_id={pessoa['id']}&crime={crime}&descricao={descricao}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201

    # 4. Listar passagens
    response = client.get(
        "/passagens",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) >= 2


def test_agente_pode_listar_passagens(client, db):
    """
    Teste: Agente pode listar passagens criminais
    Cenário: Agente tem permissão para visualizar passagens
    """
    # 1. Criar admin e fazer login
    admin, senha_admin = criar_admin(db)
    token_admin = login(client, "admin_passagem_teste", senha_admin)

    # 2. Criar pessoa e passagem (com admin)
    pessoa = criar_pessoa_para_teste(client, token_admin)

    passagem_data = criar_dados_passagem()
    response = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response.status_code == 201

    # 3. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)
    token_agente = login(client, "agente_passagem_teste", senha_agente)

    # 4. Agente lista passagens
    response = client.get(
        "/passagens",
        headers={"Authorization": f"Bearer {token_agente}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) >= 1


def test_buscar_passagem_por_id(client, db):
    """
    Teste: Buscar uma passagem específica pelo ID
    Cenário: Criar uma passagem e depois buscá-la
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar passagem
    passagem_data = criar_dados_passagem()

    response_criacao = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_criacao.status_code == 201

    passagem_criada = response_criacao.json()

    # 4. Buscar a passagem pelo ID
    response = client.get(
        f"/passagens/{passagem_criada['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == passagem_criada["id"]
    assert dados["crime"] == "Roubo"
    assert dados["pessoa_id"] == pessoa["id"]


def test_agente_pode_buscar_passagem(client, db):
    """
    Teste: Agente pode buscar uma passagem específica
    Cenário: Agente tem permissão para visualizar passagens
    """
    # 1. Criar admin e fazer login
    admin, senha_admin = criar_admin(db)
    token_admin = login(client, "admin_passagem_teste", senha_admin)

    # 2. Criar pessoa e passagem (com admin)
    pessoa = criar_pessoa_para_teste(client, token_admin)

    passagem_data = criar_dados_passagem()
    response_criacao = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response_criacao.status_code == 201
    passagem = response_criacao.json()

    # 3. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)
    token_agente = login(client, "agente_passagem_teste", senha_agente)

    # 4. Agente busca a passagem
    response = client.get(
        f"/passagens/{passagem['id']}",
        headers={"Authorization": f"Bearer {token_agente}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert dados["id"] == passagem["id"]


def test_buscar_passagem_inexistente(client, db):
    """
    Teste: Buscar uma passagem que não existe
    Cenário: Tentar buscar uma passagem com ID inválido
    """
    # 1. Criar agente e fazer login
    agente, senha = criar_agente(db)
    token = login(client, "agente_passagem_teste", senha)

    # 2. Tentar buscar passagem inexistente
    response = client.get(
        "/passagens/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Passagem criminal não encontrada."


def test_listar_passagens_por_pessoa(client, db):
    """
    Teste: Listar todas as passagens de uma pessoa específica
    Cenário: Criar uma pessoa com várias passagens e listar
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar 3 passagens para a pessoa
    passagem_data = criar_dados_passagem()
    for i in range(3):
        crime = f"Crime {i+1}"
        descricao = f"Descrição do crime {i+1}"

        response = client.post(
            f"/passagens?pessoa_id={pessoa['id']}&crime={crime}&descricao={descricao}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201

    # 4. Listar passagens da pessoa
    response = client.get(
        f"/passagens/pessoa/{pessoa['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) == 3

    # Verificar se todas as passagens são da pessoa
    for passagem in dados:
        assert passagem["pessoa_id"] == pessoa["id"]


def test_listar_passagens_por_pessoa_vazia(client, db):
    """
    Teste: Listar passagens de uma pessoa sem registros
    Cenário: Pessoa existe mas não tem passagens criminais
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa sem passagens
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Listar passagens da pessoa
    response = client.get(
        f"/passagens/pessoa/{pessoa['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Verificações - Deve retornar lista vazia
    assert response.status_code == 200
    dados = response.json()
    assert isinstance(dados, list)
    assert len(dados) == 0


def test_deletar_passagem_sucesso(client, db):
    """
    Teste: Deletar uma passagem com sucesso
    Cenário: Admin deleta uma passagem existente
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa e passagem
    pessoa = criar_pessoa_para_teste(client, token)

    passagem_data = criar_dados_passagem()
    response_criacao = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_criacao.status_code == 201
    passagem = response_criacao.json()

    # 3. Deletar passagem
    response = client.delete(
        f"/passagens/{passagem['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Verificações
    assert response.status_code == 204

    # 5. Verificar se a passagem realmente foi deletada
    response_busca = client.get(
        f"/passagens/{passagem['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response_busca.status_code == 404


def test_deletar_passagem_inexistente(client, db):
    """
    Teste: Deletar uma passagem que não existe
    Cenário: Tentar deletar com ID inválido
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Tentar deletar passagem inexistente
    response = client.delete(
        "/passagens/00000000-0000-0000-0000-000000000000",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 3. Verificações
    assert response.status_code == 404
    dados = response.json()
    assert dados["detail"] == "Passagem criminal não encontrada."


def test_agente_nao_pode_deletar_passagem(client, db):
    """
    Teste: Agente não pode deletar passagem (apenas admin)
    Cenário: Agente tenta deletar uma passagem e é bloqueado
    """
    # 1. Criar admin e fazer login
    admin, senha_admin = criar_admin(db)
    token_admin = login(client, "admin_passagem_teste", senha_admin)

    # 2. Criar pessoa e passagem (com admin)
    pessoa = criar_pessoa_para_teste(client, token_admin)

    passagem_data = criar_dados_passagem()
    response_criacao = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token_admin}"}
    )
    assert response_criacao.status_code == 201
    passagem = response_criacao.json()

    # 3. Criar agente e fazer login
    agente, senha_agente = criar_agente(db)
    token_agente = login(client, "agente_passagem_teste", senha_agente)

    # 4. Tentar deletar passagem como agente
    response = client.delete(
        f"/passagens/{passagem['id']}",
        headers={"Authorization": f"Bearer {token_agente}"}
    )

    # 5. Verificações - Deve retornar 403 ou 401 (acesso negado)
    assert response.status_code in [401, 403]


def test_passagem_tem_timestamps(client, db):
    """
    Teste: Verificar se os timestamps são criados automaticamente
    Cenário: Criar uma passagem e verificar se created_at e updated_at existem
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar passagem
    passagem_data = criar_dados_passagem()

    response = client.post(
        f"/passagens?pessoa_id={pessoa['id']}&crime={passagem_data['crime']}&descricao={passagem_data['descricao']}&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 4. Verificações
    assert response.status_code == 201
    dados = response.json()

    assert "created_at" in dados
    assert "updated_at" in dados
    assert dados["created_at"] is not None
    assert dados["updated_at"] is not None


def test_criar_multiplas_passagens_mesma_pessoa(client, db):
    """
    Teste: Criar múltiplas passagens para a mesma pessoa
    Cenário: Uma pessoa pode ter várias passagens criminais
    """
    # 1. Criar admin e fazer login
    admin, senha = criar_admin(db)
    token = login(client, "admin_passagem_teste", senha)

    # 2. Criar pessoa
    pessoa = criar_pessoa_para_teste(client, token)

    # 3. Criar 5 passagens para a mesma pessoa
    crimes = ["Roubo", "Furto", "Assalto", "Homicídio", "Tráfico"]
    passagem_data = criar_dados_passagem()

    for crime in crimes:
        response = client.post(
            f"/passagens?pessoa_id={pessoa['id']}&crime={crime}&descricao={crime} ocorrido na cidade&data_ocorrencia={passagem_data['data_ocorrencia']}&delegacia={passagem_data['delegacia']}",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 201

    # 4. Listar passagens da pessoa
    response = client.get(
        f"/passagens/pessoa/{pessoa['id']}",
        headers={"Authorization": f"Bearer {token}"}
    )

    # 5. Verificações
    assert response.status_code == 200
    dados = response.json()
    assert len(dados) == 5

    # Verificar se todos os crimes estão presentes
    crimes_encontrados = [p["crime"] for p in dados]
    for crime in crimes:
        assert crime in crimes_encontrados