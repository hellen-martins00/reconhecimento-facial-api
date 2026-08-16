import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.pessoas.model import Pessoa

class PassagemCriminal(Base):
    __tablename__ = "passagens_criminais"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("pessoas.id"),
        nullable=False
    )

    crime: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    descricao: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    data_ocorrencia: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    delegacia: Mapped[str] = mapped_column(
        String(150),
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
        back_populates="passagens_criminais"
    )