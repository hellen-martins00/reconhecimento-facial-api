from passlib.context import CryptContext

from app.agentes.repository import AgenteRepository
from app.auth.security import criar_token_acesso


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class AuthService:

    def __init__(
        self,
        repository: AgenteRepository
    ):

        self.repository = repository

    def login(
        self,
        usuario: str,
        senha: str
    ):

        agente = self.repository.buscar_por_usuario(
            usuario
        )

        if not agente:

            raise ValueError(
                "Usuário ou senha inválidos."
            )

        senha_valida = pwd_context.verify(
            senha,
            agente.senha_hash
        )

        if not senha_valida:

            raise ValueError(
                "Usuário ou senha inválidos."
            )

        token = criar_token_acesso(
            str(agente.id)
        )

        return {
            "access_token": token,
            "token_type": "bearer",
            "id": agente.id,
            "nome": agente.nome,
            "usuario": agente.usuario,
            "perfil": agente.perfil
        }