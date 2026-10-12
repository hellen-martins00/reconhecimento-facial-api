from datetime import date
from uuid import UUID

from app.desaparecimentos.model import RegistroDesaparecimento
from app.desaparecimentos.repository import (
    RegistroDesaparecimentoRepository,
)
from app.desaparecimentos.schema import RegistroDesaparecimentoUpdate


class RegistroDesaparecimentoService:

    def __init__(
        self,
        repository: RegistroDesaparecimentoRepository,
    ):
        self.repository = repository

    def criar(
        self,
        pessoa_id: UUID,
        data_desaparecimento: date,
        local_desaparecimento: str,
        descricao: str,
        status: str = "DESAPARECIDO",
    ):
        pessoa = self.repository.buscar_pessoa_por_id(pessoa_id)

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        registro = RegistroDesaparecimento(
            pessoa_id=pessoa_id,
            data_desaparecimento=data_desaparecimento,
            local_desaparecimento=local_desaparecimento,
            descricao=descricao,
            status=status,
        )

        return self.repository.salvar(registro)

    def listar(self):
        return self.repository.listar()

    def buscar_por_id(self, id: UUID):
        registro = self.repository.buscar_por_id(id)

        if not registro:
            raise ValueError(
                "Registro de desaparecimento não encontrado."
            )

        return registro

    def listar_por_pessoa(self, pessoa_id: UUID):
        pessoa = self.repository.buscar_pessoa_por_id(pessoa_id)

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        return self.repository.listar_por_pessoa(pessoa_id)

    def atualizar(
        self,
        id: UUID,
        dados: RegistroDesaparecimentoUpdate,
    ):
        registro = self.repository.buscar_por_id(id)

        if not registro:
            raise ValueError(
                "Registro de desaparecimento não encontrado."
            )

        campos = dados.model_dump(exclude_unset=True)

        for campo, valor in campos.items():
            if valor is not None:
                setattr(registro, campo, valor)

        return self.repository.atualizar(registro)

    def deletar(self, id: UUID):
        registro = self.repository.buscar_por_id(id)

        if not registro:
            raise ValueError(
                "Registro de desaparecimento não encontrado."
            )

        self.repository.deletar(registro)