import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.pessoas.model import Pessoa


class RegistroDesaparecimento(Base):
    __tablename__ = "registros_desaparecimento"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pessoas.id"),
        nullable=False,
        index=True,
    )

    data_desaparecimento: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    local_desaparecimento: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    descricao: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    pessoa: Mapped["Pessoa"] = relationship(
        back_populates="registros_desaparecimento",
    )