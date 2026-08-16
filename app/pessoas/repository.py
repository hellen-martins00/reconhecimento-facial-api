from sqlalchemy.orm import Session

from app.pessoas.model import Pessoa

class PessoaRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, pessoa: Pessoa):
        self.db.add(pessoa)
        self.db.commit()
        self.db.refresh(pessoa)
        return pessoa

    def buscar_por_cpf(self, cpf: str):
        return (
            self.db.query(Pessoa)
            .filter(Pessoa.cpf == cpf)
            .first()
        )

    def buscar_por_id(self, id):
        return (
            self.db.query(Pessoa)
            .filter(Pessoa.id == id)
            .first()
        )

    def listar(self):
        return self.db.query(Pessoa).all()
    
    def atualizar(self, pessoa: Pessoa):
        self.db.commit()
        self.db.refresh(pessoa)
        return pessoa
    
    def deletar(self, pessoa: Pessoa):
        self.db.delete(pessoa)
        self.db.commit()