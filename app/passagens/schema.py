from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PassagemCriminalResponse(BaseModel):

    id: UUID
    pessoa_id: UUID
    crime: str
    descricao: str
    data_ocorrencia: date
    delegacia: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }