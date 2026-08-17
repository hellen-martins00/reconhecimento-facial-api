import uuid
from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.fotos.model import Foto
    
class EmbeddingFacial(Base):

    __tablename__ = "embeddings_faciais"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    foto_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "fotos.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    vetor: Mapped[list[float]] = mapped_column(
        Vector(512),
        nullable=False
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    foto: Mapped["Foto"] = relationship(
        back_populates="embeddings"
    )