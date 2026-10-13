from uuid import UUID

from sqlalchemy.orm import Session

from app.localizacoes.model import LocalizacaoPessoa


class LocalizacaoPessoaRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, localizacao: LocalizacaoPessoa):
        try:
            self.db.add(localizacao)
            self.db.commit()
            self.db.refresh(localizacao)
            return localizacao

        except Exception:
            self.db.rollback()
            raise

    def buscar_por_id(self, id: UUID):
        return (
            self.db.query(LocalizacaoPessoa)
            .filter(LocalizacaoPessoa.id == id)
            .first()
        )

    def listar(self):
        return (
            self.db.query(LocalizacaoPessoa)
            .order_by(LocalizacaoPessoa.created_at.desc())
            .all()
        )

    def listar_por_registro(
        self,
        registro_desaparecimento_id: UUID,
    ):
        return (
            self.db.query(LocalizacaoPessoa)
            .filter(
                LocalizacaoPessoa.registro_desaparecimento_id
                == registro_desaparecimento_id
            )
            .order_by(LocalizacaoPessoa.data_hora.desc())
            .all()
        )