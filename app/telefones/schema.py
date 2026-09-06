from uuid import UUID

from pydantic import BaseModel, field_validator


class TelefoneCreate(BaseModel):

    pessoa_id: UUID

    numero: str

    tipo: str

    @field_validator("numero")
    @classmethod
    def validar_numero(cls, valor):

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O número do telefone é obrigatório."
            )

        if len(valor) < 8:
            raise ValueError(
                "O número do telefone deve ter pelo menos 8 caracteres."
            )

        if len(valor) > 20:
            raise ValueError(
                "O número do telefone deve ter no máximo 20 caracteres."
            )

        return valor

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor):

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O tipo do telefone é obrigatório."
            )

        if len(valor) < 3:
            raise ValueError(
                "O tipo do telefone deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 20:
            raise ValueError(
                "O tipo do telefone deve ter no máximo 20 caracteres."
            )

        return valor


class TelefoneUpdate(BaseModel):

    numero: str | None = None

    tipo: str | None = None

    @field_validator("numero")
    @classmethod
    def validar_numero(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O número do telefone não pode ficar vazio."
            )

        if len(valor) < 8:
            raise ValueError(
                "O número do telefone deve ter pelo menos 8 caracteres."
            )

        if len(valor) > 20:
            raise ValueError(
                "O número do telefone deve ter no máximo 20 caracteres."
            )

        return valor

    @field_validator("tipo")
    @classmethod
    def validar_tipo(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O tipo do telefone não pode ficar vazio."
            )

        if len(valor) < 3:
            raise ValueError(
                "O tipo do telefone deve ter pelo menos 3 caracteres."
            )

        if len(valor) > 20:
            raise ValueError(
                "O tipo do telefone deve ter no máximo 20 caracteres."
            )

        return valor


class TelefoneResponse(BaseModel):

    id: UUID

    pessoa_id: UUID

    numero: str

    tipo: str

    model_config = {
        "from_attributes": True
    }