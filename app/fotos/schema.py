from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FotoResponse(BaseModel):

    id: UUID

    pessoa_id: UUID | None = None

    agente_id: UUID | None = None

    nome_arquivo: str

    data_upload: datetime

    model_config = {
        "from_attributes": True
    }