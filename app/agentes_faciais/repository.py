from sqlalchemy.orm import Session

from app.agentes_faciais.model import AgenteFacial


class AgenteFacialRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(self, agente_facial: AgenteFacial):

        self.db.add(agente_facial)
        self.db.flush()
        self.db.refresh(agente_facial)

        return agente_facial

    def buscar_por_agente_id(self, agente_id):

        return (
            self.db.query(AgenteFacial)
            .filter(
                AgenteFacial.agente_id == agente_id
            )
            .first()
        )

    def buscar_por_id(self, id):

        return (
            self.db.query(AgenteFacial)
            .filter(
                AgenteFacial.id == id
            )
            .first()
        )

    def buscar_mais_semelhante(self, vetor):

        resultado = (
            self.db.query(
                AgenteFacial,
                AgenteFacial.vetor.cosine_distance(vetor).label(
                    "distancia"
                )
            )
            .order_by(
                AgenteFacial.vetor.cosine_distance(vetor)
            )
            .first()
        )

        return resultado