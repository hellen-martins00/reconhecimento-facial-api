from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class PassagemCriminalCreate(BaseModel):

    pessoa_id: UUID
    crime: str
    data_ocorrencia: date
    

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