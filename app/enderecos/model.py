import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, ForeignKey, DateTime

from sqlalchemy.orm import Mapped, mapped_column, relationship
    
from app.database import Base

if TYPE_CHECKING:
    from app.pessoas.model import Pessoa

class Endereco(Base):
    __tablename__ = "enderecos"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pessoas.id"),
        nullable=False
    )

    logradouro: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    numero: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    bairro: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    cidade: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    estado: Mapped[str] = mapped_column(
        String(2),
        nullable=False
    )

    cep: Mapped[str] = mapped_column(
        String(8),
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
        back_populates="enderecos"
)