import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.desaparecimentos.model import RegistroDesaparecimento


class LocalizacaoPessoa(Base):
    __tablename__ = "localizacoes_pessoa"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    registro_desaparecimento_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey(
            "registros_desaparecimento.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    local_informado: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    data_hora: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    descricao: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    registro_desaparecimento: Mapped[
        "RegistroDesaparecimento"
    ] = relationship()