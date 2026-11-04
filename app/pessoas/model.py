import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


if TYPE_CHECKING:
    from app.fotos.model import Foto
    from app.desaparecimentos.model import RegistroDesaparecimento


class Pessoa(Base):

    __tablename__ = "pessoas"

    # IDENTIFICAÇÃO

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    # DADOS PESSOAIS

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    cpf: Mapped[str | None] = mapped_column(
        String(11),
        unique=True,
        nullable=True
    )

    data_nascimento: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    sexo: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True
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

    # RELACIONAMENTOS

    fotos: Mapped[list["Foto"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )

    registros_desaparecimento: Mapped[
        list["RegistroDesaparecimento"]
    ] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )