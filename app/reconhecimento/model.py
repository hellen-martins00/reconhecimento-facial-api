import uuid

from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from app.database import Base


class Reconhecimento(Base):

    __tablename__ = "reconhecimentos"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "pessoas.id",
            ondelete="SET NULL"
        ),
        nullable=True
    )

    agente_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "agentes.id",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    reconhecido: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    distancia: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    criado_em: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    pessoa = relationship(
        "Pessoa"
    )

    agente = relationship(
        "Agente"
    )