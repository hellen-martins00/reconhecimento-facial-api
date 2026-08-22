from types import SimpleNamespace

from app.agentes.schema import AgenteCreate
from app.agentes.service import AgenteService
from app.agentes.service import pwd_context


def test_criar_agente_sucesso():

    repository = SimpleNamespace(
        buscar_por_usuario=lambda usuario: None,
        salvar=lambda agente: agente
    )

    service = AgenteService(repository)

    dados = AgenteCreate(
        nome="Agente Teste",
        usuario="agente_novo",
        senha="123456"
    )

    agente = service.criar(dados)

    assert agente.nome == "Agente Teste"
    assert agente.usuario == "agente_novo"
    assert agente.perfil == "AGENTE"

    # A senha não pode ser armazenada em texto puro
    assert agente.senha_hash != "123456"

    # O hash deve corresponder à senha informada
    assert pwd_context.verify(
        "123456",
        agente.senha_hash
    )


def test_criar_agente_usuario_duplicado():

    agente_existente = SimpleNamespace(
        usuario="agente_existente"
    )

    repository = SimpleNamespace(
        buscar_por_usuario=lambda usuario: agente_existente,
        salvar=lambda agente: agente
    )

    service = AgenteService(repository)

    dados = AgenteCreate(
        nome="Outro Agente",
        usuario="agente_existente",
        senha="123456"
    )

    try:
        service.criar(dados)

        assert False, (
            "Era esperado ValueError para usuário duplicado."
        )

    except ValueError as erro:

        assert str(erro) == (
            "Já existe um agente cadastrado com este usuário."
        )


def test_listar_agentes():

    agentes = [
        SimpleNamespace(
            nome="Agente 1",
            usuario="agente1",
            perfil="AGENTE"
        ),
        SimpleNamespace(
            nome="Agente 2",
            usuario="agente2",
            perfil="AGENTE"
        )
    ]

    repository = SimpleNamespace(
        listar=lambda: agentes
    )

    service = AgenteService(repository)

    resultado = service.listar()

    assert resultado == agentes
    assert len(resultado) == 2
    assert resultado[0].usuario == "agente1"
    assert resultado[1].usuario == "agente2"