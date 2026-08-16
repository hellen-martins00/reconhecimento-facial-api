from uuid import UUID

from pydantic import BaseModel, Field


class EnderecoCreate(BaseModel):

    pessoa_id: UUID

    logradouro: str = Field(
        ...,
        min_length=3,
        max_length=200
    )

    numero: str = Field(
        ...,
        min_length=1,
        max_length=20
    )

    bairro: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    cidade: str = Field(
        ...,
        min_length=2,
        max_length=100
    )

    estado: str = Field(
        ...,
        min_length=2,
        max_length=2
    )

    cep: str = Field(
        ...,
        min_length=8,
        max_length=8
    )


class EnderecoUpdate(BaseModel):

    logradouro: str | None = Field(
        default=None,
        min_length=3,
        max_length=200
    )

    numero: str | None = Field(
        default=None,
        min_length=1,
        max_length=20
    )

    bairro: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    cidade: str | None = Field(
        default=None,
        min_length=2,
        max_length=100
    )

    estado: str | None = Field(
        default=None,
        min_length=2,
        max_length=2
    )

    cep: str | None = Field(
        default=None,
        min_length=8,
        max_length=8
    )


class EnderecoResponse(BaseModel):

    id: UUID

    pessoa_id: UUID

    logradouro: str

    numero: str

    bairro: str

    cidade: str

    estado: str

    cep: str

    model_config = {
        "from_attributes": True
    }