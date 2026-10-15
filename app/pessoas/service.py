from uuid import UUID

from app.pessoas.model import Pessoa
from app.pessoas.repository import PessoaRepository
from app.pessoas.schema import PessoaCreate, PessoaUpdate


class PessoaService:

    def __init__(self, repository: PessoaRepository):
        self.repository = repository

    # CRIAR PESSOA

    def criar(self, dados: PessoaCreate):

        # Verifica duplicidade somente se o CPF foi informado
        if dados.cpf is not None:
            pessoa_existente = self.repository.buscar_por_cpf(
                dados.cpf
            )

            if pessoa_existente:
                raise ValueError(
                    "Já existe uma pessoa cadastrada com este CPF."
                )

        pessoa = Pessoa(
            nome=dados.nome,
            cpf=dados.cpf,
            data_nascimento=dados.data_nascimento,
            sexo=dados.sexo
        )

        return self.repository.salvar(pessoa)

    # VERIFICAR DISPONIBILIDADE DO CPF

    def cpf_disponivel(self, cpf: str):

        pessoa_existente = self.repository.buscar_por_cpf(cpf)

        return pessoa_existente is None

    # LISTAR PESSOAS

    def listar(self):

        resultados = self.repository.listar()

        return [
            {
                "id": pessoa.id,
                "nome": pessoa.nome,
                "cpf": pessoa.cpf,
                "data_nascimento": pessoa.data_nascimento,
                "sexo": pessoa.sexo,
                "foto_id": foto_id
            }
            for pessoa, foto_id in resultados
        ]

    # BUSCAR PESSOA POR ID

    def buscar_por_id(self, id: UUID):

        return self.repository.buscar_por_id(id)

    # ATUALIZAR PESSOA

    def atualizar(
        self,
        id: UUID,
        dados: PessoaUpdate
    ):

        pessoa = self.repository.buscar_por_id(id)

        if not pessoa:
            raise ValueError(
                "Pessoa não encontrada."
            )

        if dados.nome is not None:
            pessoa.nome = dados.nome

        if dados.cpf is not None:

            pessoa_existente = self.repository.buscar_por_cpf(
                dados.cpf
            )

            if (
                pessoa_existente
                and pessoa_existente.id != pessoa.id
            ):
                raise ValueError(
                    "Já existe uma pessoa cadastrada "
                    "com este CPF."
                )

            pessoa.cpf = dados.cpf

        if dados.data_nascimento is not None:
            pessoa.data_nascimento = dados.data_nascimento

        if dados.sexo is not None:
            pessoa.sexo = dados.sexo

        return self.repository.atualizar(pessoa)

    # DELETAR PESSOA

    def deletar(self, id: UUID):

        pessoa = self.repository.buscar_por_id(id)

        if not pessoa:
            raise ValueError(
                "Pessoa não encontrada."
            )

        self.repository.deletar(pessoa)