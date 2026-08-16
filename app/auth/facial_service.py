from app.agentes_faciais.repository import AgenteFacialRepository
from app.embeddings.service import EmbeddingService
from app.auth.security import criar_token_acesso


class LoginFacialService:

    def __init__(
        self,
        repository: AgenteFacialRepository
    ):
        self.repository = repository
        self.embedding_service = EmbeddingService()

    def autenticar(
        self,
        conteudo: bytes
    ):

        # 1. Gera o embedding da imagem recebida
        vetor = self.embedding_service.gerar_embedding(
            conteudo
        )

        # 2. Busca o agente facial mais semelhante
        resultado = (
            self.repository.buscar_mais_semelhante(
                vetor
            )
        )

        # 3. Nenhum agente facial cadastrado
        if not resultado:

            return {
                "autenticado": False,
                "distancia": None,
                "agente": None,
                "access_token": None
            }

        agente_facial, distancia = resultado

        # 4. Converte a distância para float
        distancia = float(distancia)

        # 5. Define o limite de reconhecimento
        threshold = 0.5

        # 6. Verifica se a distância está dentro do limite
        if distancia > threshold:

            return {
                "autenticado": False,
                "distancia": distancia,
                "agente": None,
                "access_token": None
            }

        # 7. Recupera o agente relacionado ao vetor facial
        agente = agente_facial.agente

        # 8. Gera o token JWT
        token = criar_token_acesso(
            str(agente.id)
        )

        # 9. Retorna o resultado da autenticação
        return {
            "autenticado": True,
            "distancia": distancia,
            "agente": agente,
            "access_token": token
        }