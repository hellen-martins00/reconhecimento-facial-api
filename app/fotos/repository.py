from uuid import UUID

from sqlalchemy.orm import Session

from app.fotos.model import Foto


class FotoRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, foto: Foto):
        self.db.add(foto)
        self.db.flush()
        self.db.refresh(foto)

        return foto

    def buscar_por_id(self, id: UUID):
        return (
            self.db.query(Foto)
            .filter(Foto.id == id)
            .first()
        )

    def listar(self):
        return self.db.query(Foto).all()

    def buscar_por_pessoa(self, pessoa_id: UUID):
        return (
            self.db.query(Foto)
            .filter(Foto.pessoa_id == pessoa_id)
            .all()
        )
        
    def buscar_por_agente(self, agente_id: UUID):
        return (
            self.db.query(Foto)
            .filter(Foto.agente_id == agente_id)
            .all()
        )    

    def deletar(self, foto: Foto):
        self.db.delete(foto)
        self.db.commit()