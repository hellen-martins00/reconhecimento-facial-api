from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AgenteFacialResponse(BaseModel):

    id: UUID

    agente_id: UUID

    created_at: datetime

    model_config = {
        "from_attributes": True
    }