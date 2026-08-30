from sqlalchemy.orm import Session

from app.reconhecimento.model import Reconhecimento


class ReconhecimentoRepository:

    def __init__(self, db: Session):
        self.db = db

    def criar(
        self,
        reconhecimento: Reconhecimento
    ):

        self.db.add(reconhecimento)

        self.db.commit()

        self.db.refresh(reconhecimento)

        return reconhecimento


    def contar_total(self):

        return (
            self.db
            .query(Reconhecimento)
            .count()
        )


    def listar_ultimos(self, limite: int = 5):

        return (
            self.db
            .query(Reconhecimento)
            .order_by(
                Reconhecimento.criado_em.desc()
            )
            .limit(limite)
            .all()
        )