import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.agentes.model import Agente


class AgenteFacial(Base):

    __tablename__ = "agentes_faciais"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    agente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agentes.id"),
        nullable=False,
        unique=True
    )

    vetor: Mapped[list[float]] = mapped_column(
        Vector(512),
        nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    agente: Mapped["Agente"] = relationship(
        back_populates="facial"
    )