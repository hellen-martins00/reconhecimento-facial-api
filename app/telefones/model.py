import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.pessoas.model import Pessoa

class Telefone(Base):
    __tablename__ = "telefones"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pessoas.id"),
        nullable=False
    )

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    pessoa: Mapped["Pessoa"] = relationship(
        back_populates="telefones"
    )