from uuid import UUID

from sqlalchemy.orm import Session

from app.desaparecimentos.model import RegistroDesaparecimento
from app.pessoas.model import Pessoa


class RegistroDesaparecimentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, registro: RegistroDesaparecimento):
        try:
            self.db.add(registro)
            self.db.commit()
            self.db.refresh(registro)
            return registro

        except Exception:
            self.db.rollback()
            raise

    def buscar_por_id(self, id: UUID):
        return (
            self.db.query(RegistroDesaparecimento)
            .filter(RegistroDesaparecimento.id == id)
            .first()
        )

    def listar(self):
        return self.db.query(RegistroDesaparecimento).all()

    def listar_por_pessoa(self, pessoa_id: UUID):
        return (
            self.db.query(RegistroDesaparecimento)
            .filter(
                RegistroDesaparecimento.pessoa_id == pessoa_id
            )
            .all()
        )

    def buscar_pessoa_por_id(self, pessoa_id: UUID):
        return (
            self.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

    def atualizar(self, registro: RegistroDesaparecimento):
        try:
            self.db.commit()
            self.db.refresh(registro)
            return registro

        except Exception:
            self.db.rollback()
            raise

    def deletar(self, registro: RegistroDesaparecimento):
        try:
            self.db.delete(registro)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise