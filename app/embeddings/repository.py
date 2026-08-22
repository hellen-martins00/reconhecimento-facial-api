import uuid

from sqlalchemy.orm import Session

from app.embeddings.model import EmbeddingFacial


class EmbeddingRepository:

    def __init__(self, db: Session):
        self.db = db

    def salvar(
        self,
        foto_id,
        vetor: list[float]
    ):

        embedding = EmbeddingFacial(
            foto_id=foto_id,
            vetor=vetor
        )

        self.db.add(embedding)
        self.db.flush()
        self.db.refresh(embedding)

        return embedding

    def buscar_por_foto_id(
        self,
        foto_id: uuid.UUID
    ):

        return (
            self.db.query(EmbeddingFacial)
            .filter(
                EmbeddingFacial.foto_id == foto_id
            )
            .first()
        )

    def buscar_mais_semelhante(
        self,
        vetor: list[float]
    ):

        resultado = (
            self.db.query(
                EmbeddingFacial,
                EmbeddingFacial.vetor.cosine_distance(
                    vetor
                ).label("distancia")
            )
            .order_by(
                EmbeddingFacial.vetor.cosine_distance(
                    vetor
                )
            )
            .first()
        )

        return resultado