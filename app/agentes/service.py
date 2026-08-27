from passlib.context import CryptContext

from app.agentes.model import Agente
from app.agentes.repository import AgenteRepository
from app.agentes.schema import AgenteCreate, AgenteUpdate


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
            perfil=dados.perfil
        )

        return self.repository.salvar(agente)

    def listar(self):

        return self.repository.listar()

    def buscar_por_id(self, id):

        return self.repository.buscar_por_id(id)

    def atualizar(self, id, dados: AgenteUpdate):

        agente = self.repository.buscar_por_id(id)

        if not agente:
            raise ValueError(
                "Agente não encontrado."
            )

        if dados.nome is not None:
            agente.nome = dados.nome

        if dados.usuario is not None:

            existente = (
                self.repository.buscar_por_usuario(
                    dados.usuario
                )
            )

            if existente and existente.id != agente.id:
                raise ValueError(
                    "Já existe um agente cadastrado "
                    "com este usuário."
                )

            agente.usuario = dados.usuario

        if dados.senha is not None:

            agente.senha_hash = pwd_context.hash(
                dados.senha
            )

        return self.repository.atualizar(agente)

    def deletar(self, id):

        agente = self.repository.buscar_por_id(id)

        if not agente:
            raise ValueError(
                "Agente não encontrado."
            )

        self.repository.deletar(agente)