from passlib.context import CryptContext

from app.agentes.model import Agente
from app.agentes.repository import AgenteRepository
from app.agentes.schema import AgenteCreate


pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class AgenteService:

    def __init__(self, repository: AgenteRepository):

        self.repository = repository

    def criar(self, dados: AgenteCreate):

        agente_existente = (
            self.repository.buscar_por_usuario(
                dados.usuario
            )
        )

        if agente_existente:

            raise ValueError(
                "Já existe um agente cadastrado com este usuário."
            )

        senha_hash = pwd_context.hash(
            dados.senha
        )

        agente = Agente(
            nome=dados.nome,
            usuario=dados.usuario,
            senha_hash=senha_hash,
            perfil="AGENTE"
        )

        return self.repository.salvar(agente)

    def listar(self):

        return self.repository.listar()