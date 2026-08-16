from uuid import UUID

from pydantic import BaseModel, Field


class TelefoneCreate(BaseModel):

    pessoa_id: UUID

    numero: str = Field(
        ...,
        min_length=8,
        max_length=20
    )

    tipo: str = Field(
        ...,
        min_length=3,
        max_length=20
    )


class TelefoneUpdate(BaseModel):

    numero: str | None = Field(
        default=None,
        min_length=8,
        max_length=20
    )

    tipo: str | None = Field(
        default=None,
        min_length=3,
        max_length=20
    )


class TelefoneResponse(BaseModel):

    id: UUID

    pessoa_id: UUID

    numero: str

    tipo: str

    model_config = {
        "from_attributes": True
    }