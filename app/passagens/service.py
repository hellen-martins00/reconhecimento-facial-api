import uuid
from datetime import date

from app.passagens.model import PassagemCriminal
from app.passagens.repository import PassagemRepository
from app.pessoas.model import Pessoa


class PassagemService:

    def __init__(
        self,
        repository: PassagemRepository
    ):
        self.repository = repository

    def criar(
        self,
        pessoa_id: uuid.UUID,
        crime: str,
        data_ocorrencia: date
    ):

        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError(
                "Pessoa não encontrada."
            )

        passagem = PassagemCriminal(
            pessoa_id=pessoa_id,
            crime=crime,
            data_ocorrencia=data_ocorrencia
        )

        return self.repository.salvar(passagem)

    def listar(self):

        return self.repository.listar()

    def buscar_por_id(self, id):

        passagem = self.repository.buscar_por_id(id)

        if not passagem:
            raise ValueError(
                "Passagem criminal não encontrada."
            )

        return passagem

    def listar_por_pessoa(self, pessoa_id):

        return self.repository.listar_por_pessoa(
            pessoa_id
        )

    def deletar(self, id):

        passagem = self.repository.buscar_por_id(id)

        if not passagem:
            raise ValueError(
                "Passagem criminal não encontrada."
            )

        self.repository.deletar(passagem)