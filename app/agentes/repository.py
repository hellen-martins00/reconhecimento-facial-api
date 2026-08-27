from sqlalchemy.orm import Session

from app.agentes.model import Agente


class AgenteRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, agente: Agente):

        self.db.add(agente)

        self.db.commit()

        self.db.refresh(agente)

        return agente

    def buscar_por_usuario(self, usuario: str):

        return (
            self.db.query(Agente)
            .filter(Agente.usuario == usuario)
            .first()
        )

    def buscar_por_id(self, id):

        return (
            self.db.query(Agente)
            .filter(Agente.id == id)
            .first()
        )

    def listar(self):

        return self.db.query(Agente).all()
    
    def atualizar(self, agente: Agente):
        self.db.commit()

        self.db.refresh(agente)

        return agente
    
    def deletar(self, agente: Agente):
            self.db.delete(agente)
            self.db.commit()