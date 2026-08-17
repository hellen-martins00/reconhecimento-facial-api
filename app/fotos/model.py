import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, DateTime, String, LargeBinary, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.pessoas.model import Pessoa
    from app.embeddings.model import EmbeddingFacial
    from app.agentes.model import Agente


class Foto(Base):

    __tablename__ = "fotos"
    
    __table_args__ = (
        CheckConstraint(
            """
            (pessoa_id IS NOT NULL AND agente_id IS NULL)
            OR
            (pessoa_id IS NULL AND agente_id IS NOT NULL)
            """,
            name="ck_foto_um_unico_dono"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    pessoa_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "pessoas.id",
            ondelete="CASCADE",
        ),
        nullable=True
    )

    agente_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey(
            "agentes.id",
            ondelete="CASCADE"
        ),
        nullable=True
    )

    nome_arquivo: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    arquivo: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False
    )

    data_upload: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
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
        back_populates="fotos"
    )
    
    agente: Mapped["Agente"] = relationship(
        back_populates="fotos"
    )

    embeddings: Mapped[list["EmbeddingFacial"]] = relationship(
        back_populates="foto",
        cascade="all, delete-orphan"
    )