from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


class PassagemCriminalCreate(BaseModel):

    pessoa_id: UUID
    crime: str
    data_ocorrencia: date

    @field_validator("crime")
    @classmethod
    def validar_crime(cls, valor):

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O crime é obrigatório."
            )

        if len(valor) < 3:
            raise ValueError(
                "O crime deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 150:
            raise ValueError(
                "O crime deve ter no máximo 150 caracteres."
            )

        return valor


class PassagemCriminalUpdate(BaseModel):

    crime: str | None = None
    data_ocorrencia: date | None = None

    @field_validator("crime")
    @classmethod
    def validar_crime(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O crime é obrigatório."
            )

        if len(valor) < 3:
            raise ValueError(
                "O crime deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 150:
            raise ValueError(
                "O crime deve ter no máximo 150 caracteres."
            )

        return valor


class PassagemCriminalResponse(BaseModel):

    id: UUID
    pessoa_id: UUID
    crime: str
    data_ocorrencia: date
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }