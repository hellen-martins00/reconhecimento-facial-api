from datetime import datetime
from uuid import UUID

from app.desaparecimentos.repository import (
    RegistroDesaparecimentoRepository,
)
from app.localizacoes.model import LocalizacaoPessoa
from app.localizacoes.repository import (
    LocalizacaoPessoaRepository,
)


class LocalizacaoPessoaService:

    def __init__(
        self,
        repository: LocalizacaoPessoaRepository,
        desaparecimento_repository: RegistroDesaparecimentoRepository,
    ):
        self.repository = repository
        self.desaparecimento_repository = (
            desaparecimento_repository
        )

    def criar(
        self,
        registro_desaparecimento_id: UUID,
        local_informado: str,
        data_hora: datetime,
        descricao: str | None = None,
    ):
        registro = (
            self.desaparecimento_repository.buscar_por_id(
                registro_desaparecimento_id
            )
        )

        if not registro:
            raise ValueError(
                "Registro de desaparecimento não encontrado."
            )

        localizacao = LocalizacaoPessoa(
            registro_desaparecimento_id=registro_desaparecimento_id,
            local_informado=local_informado,
            data_hora=data_hora,
            descricao=descricao,
        )

        return self.repository.salvar(localizacao)

    def listar(self):
        return self.repository.listar()

    def buscar_por_id(self, id: UUID):
        localizacao = self.repository.buscar_por_id(id)

        if not localizacao:
            raise ValueError(
                "Localização não encontrada."
            )

        return localizacao

    def listar_por_registro(
        self,
        registro_desaparecimento_id: UUID,
    ):
        registro = (
            self.desaparecimento_repository.buscar_por_id(
                registro_desaparecimento_id
            )
        )

        if not registro:
            raise ValueError(
                "Registro de desaparecimento não encontrado."
            )

        return self.repository.listar_por_registro(
            registro_desaparecimento_id
        )