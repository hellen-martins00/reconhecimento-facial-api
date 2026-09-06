from uuid import UUID

from sqlalchemy.orm import Session

from app.passagens.model import PassagemCriminal
from app.pessoas.model import Pessoa


class PassagemRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, passagem: PassagemCriminal):

        try:
            self.db.add(passagem)
            self.db.commit()
            self.db.refresh(passagem)

            return passagem

        except Exception:
            self.db.rollback()
            raise

    def buscar_por_id(self, id: UUID):

        return (
            self.db.query(PassagemCriminal)
            .filter(PassagemCriminal.id == id)
            .first()
        )

    def listar(self):

        return (
            self.db.query(PassagemCriminal)
            .all()
        )

    def listar_por_pessoa(self, pessoa_id: UUID):

        return (
            self.db.query(PassagemCriminal)
            .filter(
                PassagemCriminal.pessoa_id == pessoa_id
            )
            .all()
        )

    def buscar_pessoa_por_id(self, pessoa_id: UUID):

        return (
            self.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )
        
    def atualizar(self, passagem: PassagemCriminal):
        try:
            self.db.commit()
            self.db.refresh(passagem)

            return passagem

        except Exception:
            self.db.rollback()
            raise

    def deletar(self, passagem: PassagemCriminal):

        try:
            self.db.delete(passagem)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise