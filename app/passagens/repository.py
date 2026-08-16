from uuid import UUID

from sqlalchemy.orm import Session

from app.passagens.model import PassagemCriminal


class PassagemRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, passagem: PassagemCriminal):

        self.db.add(passagem)
        self.db.commit()
        self.db.refresh(passagem)

        return passagem

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

    def deletar(self, passagem: PassagemCriminal):

        self.db.delete(passagem)
        self.db.commit()