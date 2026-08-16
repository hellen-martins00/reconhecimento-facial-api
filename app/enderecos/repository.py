from uuid import UUID

from sqlalchemy.orm import Session

from app.enderecos.model import Endereco


class EnderecoRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, endereco: Endereco):
        self.db.add(endereco)
        self.db.commit()
        self.db.refresh(endereco)

        return endereco

    def buscar_por_id(self, id: UUID):
        return (
            self.db.query(Endereco)
            .filter(Endereco.id == id)
            .first()
        )

    def listar(self):
        return self.db.query(Endereco).all()

    def buscar_por_pessoa(self, pessoa_id: UUID):
        return (
            self.db.query(Endereco)
            .filter(Endereco.pessoa_id == pessoa_id)
            .all()
        )

    def atualizar(self, endereco: Endereco):
        self.db.commit()
        self.db.refresh(endereco)

        return endereco

    def deletar(self, endereco: Endereco):
        self.db.delete(endereco)
        self.db.commit()