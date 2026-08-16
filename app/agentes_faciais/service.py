from app.agentes_faciais.model import AgenteFacial
from app.agentes_faciais.repository import AgenteFacialRepository
from app.embeddings.service import EmbeddingService


class AgenteFacialService:

    def __init__(
        self,
        repository: AgenteFacialRepository
    ):
        self.repository = repository
        self.embedding_service = EmbeddingService()

    def cadastrar(
        self,
        agente_id,
        conteudo: bytes
    ):

        # Verifica se o agente já possui cadastro facial
        existente = (
            self.repository.buscar_por_agente_id(
                agente_id
            )
        )

        if existente:

            raise ValueError(
                "Este agente já possui um cadastro facial."
            )

        # Gera o embedding facial
        vetor = self.embedding_service.gerar_embedding(
            conteudo
        )

        # Cria o registro
        agente_facial = AgenteFacial(
            agente_id=agente_id,
            vetor=vetor
        )

        return self.repository.salvar(
            agente_facial
        )