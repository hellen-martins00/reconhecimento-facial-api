from uuid import UUID

from sqlalchemy.orm import Session

from app.telefones.model import Telefone


class TelefoneRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, telefone: Telefone):
        self.db.add(telefone)
        self.db.commit()
        self.db.refresh(telefone)

        return telefone

    def buscar_por_id(self, id: UUID):
        return (
            self.db.query(Telefone)
            .filter(Telefone.id == id)
            .first()
        )

    def listar(self):
        return self.db.query(Telefone).all()

    def buscar_por_pessoa(self, pessoa_id: UUID):
        return (
            self.db.query(Telefone)
            .filter(Telefone.pessoa_id == pessoa_id)
            .all()
        )

    def atualizar(self, telefone: Telefone):
        self.db.commit()
        self.db.refresh(telefone)

        return telefone

    def deletar(self, telefone: Telefone):
        self.db.delete(telefone)
        self.db.commit()