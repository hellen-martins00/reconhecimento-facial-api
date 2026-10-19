
from datetime import datetime
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    field_validator,
)


class LocalizacaoPessoaCreate(BaseModel):
    registro_desaparecimento_id: UUID
    local_informado: str
    latitude: float | None = None
    longitude: float | None = None
    data_hora: datetime
    descricao: str | None = None

    @field_validator("local_informado")
    @classmethod
    def validar_local(cls, valor: str):
        valor = valor.strip()

        if not 3 <= len(valor) <= 200:
            raise ValueError(
                "O local deve ter entre 3 e 200 caracteres."
            )

        return valor

    @field_validator("latitude")
    @classmethod
    def validar_latitude(cls, valor: float | None):
        if valor is not None and not -90 <= valor <= 90:
            raise ValueError("Latitude inválida.")
        return valor

    @field_validator("longitude")
    @classmethod
    def validar_longitude(cls, valor: float | None):
        if valor is not None and not -180 <= valor <= 180:
            raise ValueError("Longitude inválida.")
        return valor

    @field_validator("descricao")
    @classmethod
    def validar_descricao(cls, valor: str | None):
        if valor is None:
            return valor

        valor = valor.strip()

        if len(valor) > 2000:
            raise ValueError(
                "A descrição deve ter no máximo 2000 caracteres."
            )

        return valor or None

    @field_validator("data_hora")
    @classmethod
    def validar_data_hora(cls, valor: datetime):
        if valor > datetime.now():
            raise ValueError(
                "A data e hora do avistamento não podem ser futuras."
            )

        return valor


class LocalizacaoPessoaResponse(BaseModel):
    id: UUID
    registro_desaparecimento_id: UUID
    local_informado: str
    latitude: float | None
    longitude: float | None
    data_hora: datetime
    descricao: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
