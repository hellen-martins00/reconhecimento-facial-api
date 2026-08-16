from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class LoginRequest(BaseModel):

    usuario: str

    senha: str


class LoginResponse(BaseModel):

    access_token: str

    token_type: str

    id: UUID

    nome: str

    usuario: str


class LoginFacialResponse(BaseModel):

    autenticado: bool

    distancia: Optional[float] = None

    access_token: Optional[str] = None

    token_type: Optional[str] = None

    id: Optional[UUID] = None

    nome: Optional[str] = None

    usuario: Optional[str] = None