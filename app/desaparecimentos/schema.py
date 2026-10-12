from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator


class RegistroDesaparecimentoCreate(BaseModel):
    pessoa_id: UUID
    data_desaparecimento: date
    local_desaparecimento: str
    descricao: str

    @field_validator("data_desaparecimento")
    @classmethod
    def validar_data(cls, valor: date):
        if valor > date.today():
            raise ValueError(
                "A data do desaparecimento não pode ser futura."
            )
        return valor

    @field_validator("local_desaparecimento")
    @classmethod
    def validar_local(cls, valor: str):
        valor = valor.strip()

        if len(valor) < 3:
            raise ValueError(
                "O local deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 200:
            raise ValueError(
                "O local deve ter no máximo 200 caracteres."
            )

        return valor

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, valor: str):
        valor = valor.strip()

        if len(valor) < 3:
            raise ValueError(
                "A descrição deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 500:
            raise ValueError(
                "A descrição deve ter no máximo 500 caracteres."
            )

        return valor


class RegistroDesaparecimentoUpdate(BaseModel):
    data_desaparecimento: date | None = None
    local_desaparecimento: str | None = None
    descricao: str | None = None

    @field_validator("data_desaparecimento")
    @classmethod
    def validar_data(cls, valor: date | None):
        if valor is not None and valor > date.today():
            raise ValueError(
                "A data do desaparecimento não pode ser futura."
            )
        return valor

    @field_validator("local_desaparecimento")
    @classmethod
    def validar_local(cls, valor: str | None):
        if valor is None:
            return valor

        valor = valor.strip()

        if not 3 <= len(valor) <= 200:
            raise ValueError(
                "O local deve ter entre 3 e 200 caracteres."
            )

        return valor

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, valor: str | None):
        if valor is None:
            return valor

        valor = valor.strip()

        if not 3 <= len(valor) <= 500:
            raise ValueError(
                "A descrição deve ter entre 3 e 500 caracteres."
            )

        return valor


class RegistroDesaparecimentoResponse(BaseModel):
    id: UUID
    pessoa_id: UUID
    data_desaparecimento: date
    local_desaparecimento: str
    descricao: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)