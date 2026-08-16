import uuid
from datetime import datetime, date
from typing import TYPE_CHECKING

from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.telefones.model import Telefone
    from app.enderecos.model import Endereco
    from app.fotos.model import Foto
    from app.passagens.model import PassagemCriminal

class Pessoa(Base):
    __tablename__ = "pessoas"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )

    nome: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    cpf: Mapped[str] = mapped_column(
        String(11),
        unique=True,
        nullable=False
    )

    data_nascimento: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    sexo: Mapped[str] = mapped_column(
        String(1),
        nullable=False
    )

    nome_mae: Mapped[str] = mapped_column(
        String(150)
    )

    nome_pai: Mapped[str] = mapped_column(
        String(150)
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

    # relacionamentos
    telefones: Mapped[list["Telefone"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )
    
    enderecos: Mapped[list["Endereco"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )
    
    fotos: Mapped[list["Foto"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )
    
    passagens_criminais: Mapped[list["PassagemCriminal"]] = relationship(
        back_populates="pessoa",
        cascade="all, delete-orphan"
    )