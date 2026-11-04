
from datetime import datetime, timedelta
from uuid import uuid4

from app.agentes.model import Agente
from app.auth.service import pwd_context
from app.desaparecimentos.model import RegistroDesaparecimento
from app.pessoas.model import Pessoa


def criar_admin(db):
    senha = "123456"

    admin = Agente(
        nome="Administrador Localização",
        usuario="admin_localizacao_teste",
        senha_hash=pwd_context.hash(senha),
        perfil="ADMIN"
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin, senha


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



def criar_registro_desaparecimento(db):
    pessoa = Pessoa(
        nome="Pessoa Desaparecida Teste",
        cpf=str(uuid4().int)[:11],
        data_nascimento=datetime(1990, 1, 1).date(),
        sexo="F"
    )

    db.add(pessoa)
    db.commit()
    db.refresh(pessoa)

    registro = RegistroDesaparecimento(
        pessoa_id=pessoa.id,
        data_desaparecimento=(
            datetime.now().date() - timedelta(days=5)
        ),
        local_desaparecimento="Brasília - DF",
        descricao="Registro utilizado nos testes",
        status="DESAPARECIDO"
    )

    db.add(registro)
    db.commit()
    db.refresh(registro)

    return registro

def criar_dados_localizacao(registro_id):
    return {
        "registro_desaparecimento_id": str(registro_id),
        "local_informado": "Rodoviária de Brasília",
        "latitude": -15.793889,
        "longitude": -47.882778,
        "data_hora": (
            datetime.now() - timedelta(hours=2)
        ).isoformat(),
        "descricao": "Pessoa avistada próximo à entrada principal."
    }


def test_criar_localizacao_sucesso(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_localizacao(registro.id)
    )

    assert response.status_code == 201

    dados = response.json()

    assert "id" in dados
    assert dados["registro_desaparecimento_id"] == str(registro.id)
    assert dados["local_informado"] == "Rodoviária de Brasília"
    assert dados["latitude"] == -15.793889
    assert dados["longitude"] == -47.882778


def test_criar_localizacao_registro_inexistente(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    dados = criar_dados_localizacao(uuid4())

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Registro de desaparecimento não encontrado."
    )


def test_listar_localizacoes(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    response = client.get(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_listar_localizacoes_por_registro(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_localizacao(registro.id)
    )

    response = client.get(
        f"/localizacoes/registro/{registro.id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_listar_localizacoes_registro_inexistente(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro_id = uuid4()

    response = client.get(
        f"/localizacoes/registro/{registro_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Registro de desaparecimento não encontrado."
    )


def test_excluir_localizacao_sucesso(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    criacao = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=criar_dados_localizacao(registro.id)
    )

    assert criacao.status_code == 201

    localizacao_id = criacao.json()["id"]

    response = client.delete(
        f"/localizacoes/{localizacao_id}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 204


def test_excluir_localizacao_inexistente(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    response = client.delete(
        f"/localizacoes/{uuid4()}",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )

    assert response.status_code == 404

    assert response.json()["detail"] == (
        "Localização não encontrada."
    )


def test_criar_localizacao_sem_autenticacao(client, db):
    registro = criar_registro_desaparecimento(db)

    response = client.post(
        "/localizacoes",
        json=criar_dados_localizacao(registro.id)
    )

    assert response.status_code == 401


def test_criar_localizacao_latitude_invalida(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    dados = criar_dados_localizacao(registro.id)
    dados["latitude"] = 100

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 422


def test_criar_localizacao_longitude_invalida(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    dados = criar_dados_localizacao(registro.id)
    dados["longitude"] = 200

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 422


def test_criar_localizacao_data_futura(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    dados = criar_dados_localizacao(registro.id)
    dados["data_hora"] = (
        datetime.now() + timedelta(days=1)
    ).isoformat()

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 422


def test_criar_localizacao_local_invalido(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    dados = criar_dados_localizacao(registro.id)
    dados["local_informado"] = "AB"

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 422


def test_criar_localizacao_descricao_excedida(client, db):
    admin, senha = criar_admin(db)

    token = login(
        client,
        "admin_localizacao_teste",
        senha
    )

    registro = criar_registro_desaparecimento(db)

    dados = criar_dados_localizacao(registro.id)
    dados["descricao"] = "A" * 2001

    response = client.post(
        "/localizacoes",
        headers={
            "Authorization": f"Bearer {token}"
        },
        json=dados
    )

    assert response.status_code == 422
