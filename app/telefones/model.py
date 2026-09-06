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

    # IDENTIFICAÇÃO

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pessoas.id"),
        nullable=False
    )

    # DADOS DO TELEFONE

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    tipo: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    # CONTROLE

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # RELACIONAMENTO

    pessoa: Mapped["Pessoa"] = relationship(
        back_populates="telefones"
    )