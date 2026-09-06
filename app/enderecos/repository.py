from uuid import UUID

from sqlalchemy.orm import Session

from app.enderecos.model import Endereco
from app.pessoas.model import Pessoa


class EnderecoRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, endereco: Endereco):
        try:
            self.db.add(endereco)
            self.db.commit()
            self.db.refresh(endereco)

            return endereco

        except Exception:
            self.db.rollback()
            raise

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

    def buscar_pessoa_por_id(self, pessoa_id: UUID):
        return (
            self.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

    def atualizar(self, endereco: Endereco):
        try:
            self.db.commit()
            self.db.refresh(endereco)

            return endereco

        except Exception:
            self.db.rollback()
            raise

    def deletar(self, endereco: Endereco):
        try:
            self.db.delete(endereco)
            self.db.commit()

        except Exception:
            self.db.rollback()
            raise