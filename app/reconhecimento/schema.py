from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class PessoaReconhecimentoResponse(BaseModel):

    id: UUID
    nome: str
    cpf: str


class FotoReconhecimentoResponse(BaseModel):

    id: UUID
    nome_arquivo: str
    data_upload: datetime


class ReconhecimentoResponse(BaseModel):

    reconhecido: bool
    distancia: float | None
    pessoa: PessoaReconhecimentoResponse | None
    foto: FotoReconhecimentoResponse | None