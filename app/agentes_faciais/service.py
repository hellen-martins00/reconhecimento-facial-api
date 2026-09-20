from app.agentes_faciais.model import AgenteFacial
from app.agentes_faciais.repository import AgenteFacialRepository
from app.embeddings.service import EmbeddingService


class AgenteFacialService:

    DISTANCIA_MAXIMA = 0.5

    def __init__(
        self,
        repository: AgenteFacialRepository
    ):
        self.repository = repository
        self.embedding_service = EmbeddingService()

    def _verificar_rosto_duplicado(
        self,
        vetor,
        agente_id_atual=None
    ):
        resultado = (
            self.repository.buscar_mais_semelhante(
                vetor,
                agente_id_excluir=agente_id_atual
            )
        )

        if not resultado:
            return

        agente_facial, distancia = resultado

        if distancia <= self.DISTANCIA_MAXIMA:

            raise ValueError(
                "Esta foto facial já está cadastrada para outro agente."
            )

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

        # Verifica se esse rosto já pertence a outro agente
        self._verificar_rosto_duplicado(
            vetor
        )

        # Cria o registro
        agente_facial = AgenteFacial(
            agente_id=agente_id,
            vetor=vetor
        )

        return self.repository.salvar(
            agente_facial
        )