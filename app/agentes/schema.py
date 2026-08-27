from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AgenteCreate(BaseModel):

    nome: str = Field(
        ...,
        min_length=3,
        max_length=150
    )

    usuario: str = Field(
        ...,
        min_length=3,
        max_length=100
    )

    senha: str = Field(
        ...,
        min_length=6,
        max_length=100
    )
    
    perfil: str = Field(
        default="AGENTE"
    )


class AgenteUpdate(BaseModel):

    nome: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150
    )

    usuario: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100
    )

    senha: Optional[str] = Field(
        None,
        min_length=6,
        max_length=100
    )


class AgenteResponse(BaseModel):

    id: UUID

    nome: str

    usuario: str

    perfil: str

    created_at: datetime

    updated_at: datetime

    model_config = {
        "from_attributes": True
    }