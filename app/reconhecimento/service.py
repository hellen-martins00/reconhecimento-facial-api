from app.embeddings.repository import EmbeddingRepository
from app.embeddings.service import EmbeddingService


class ReconhecimentoService:

    def __init__(self, repository: EmbeddingRepository):
        self.repository = repository
        self.embedding_service = EmbeddingService()

    def reconhecer(
        self,
        conteudo: bytes
    ):

        # 1. Gerar embedding diretamente dos bytes da imagem
        vetor = self.embedding_service.gerar_embedding(
            conteudo
        )

        # 2. Buscar o embedding mais semelhante no banco
        resultado = self.repository.buscar_mais_semelhante(
            vetor
        )

        # 3. Nenhum embedding cadastrado
        if not resultado:
            return {
                "reconhecido": False,
                "distancia": None,
                "pessoa": None,
                "foto": None
            }

        embedding, distancia = resultado

        # 4. Threshold provisório
        threshold = 0.5

        # 5. Verificar se é suficientemente semelhante
        if distancia > threshold:
            return {
                "reconhecido": False,
                "distancia": float(distancia),
                "pessoa": None,
                "foto": None
            }

        # 6. Buscar a foto relacionada
        foto = embedding.foto

        # 7. Buscar a pessoa relacionada
        pessoa = foto.pessoa

        return {
            "reconhecido": True,
            "distancia": float(distancia),
            "pessoa": pessoa,
            "foto": foto
        }