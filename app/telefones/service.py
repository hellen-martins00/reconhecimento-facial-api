from uuid import UUID

from app.pessoas.model import Pessoa
from app.telefones.model import Telefone
from app.telefones.repository import TelefoneRepository
from app.telefones.schema import TelefoneCreate, TelefoneUpdate


class TelefoneService:

    def __init__(self, repository: TelefoneRepository):
        self.repository = repository

    def criar(self, dados: TelefoneCreate):

        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == dados.pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        telefone = Telefone(
            pessoa_id=dados.pessoa_id,
            numero=dados.numero,
            tipo=dados.tipo
        )

        return self.repository.salvar(telefone)

    def listar(self):
        return self.repository.listar()

    def buscar_por_id(self, id: UUID):

        telefone = self.repository.buscar_por_id(id)

        if not telefone:
            raise ValueError("Telefone não encontrado.")

        return telefone

    def listar_por_pessoa(self, pessoa_id: UUID):

        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        return self.repository.buscar_por_pessoa(pessoa_id)

    def atualizar(self, id: UUID, dados: TelefoneUpdate):

        telefone = self.repository.buscar_por_id(id)

        if not telefone:
            raise ValueError("Telefone não encontrado.")

        if dados.numero is not None:
            telefone.numero = dados.numero

        if dados.tipo is not None:
            telefone.tipo = dados.tipo

        return self.repository.atualizar(telefone)

    def deletar(self, id: UUID):

        telefone = self.repository.buscar_por_id(id)

        if not telefone:
            raise ValueError("Telefone não encontrado.")

        self.repository.deletar(telefone)