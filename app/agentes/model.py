import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.agentes_faciais.model import AgenteFacial
    from app.fotos.model import Foto


class Agente(Base):

    __tablename__ = "agentes"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    usuario: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    senha_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    perfil: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="AGENTE"
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

    # Vetor facial utilizado no reconhecimento/login
    facial: Mapped["AgenteFacial"] = relationship(
        back_populates="agente",
        cascade="all, delete-orphan",
        uselist=False
    )

    # Fotos do agente
    fotos: Mapped[list["Foto"]] = relationship(
        back_populates="agente",
        cascade="all, delete-orphan"
    )