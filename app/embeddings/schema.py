from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

class EmbeddingResponse(BaseModel):

    id: UUID

    foto_id: UUID

    vetor: list[float]

    created_at: datetime

    model_config = {
        "from_attributes": True
    }