import uuid
from pathlib import Path

from app.fotos.model import Foto
from app.fotos.repository import FotoRepository
from app.pessoas.model import Pessoa
from app.agentes.model import Agente
from app.agentes_faciais.model import AgenteFacial

from app.embeddings.service import EmbeddingService
from app.embeddings.repository import EmbeddingRepository


class FotoService:

    def __init__(
        self,
        repository: FotoRepository,
        embedding_service: EmbeddingService,
        embedding_repository: EmbeddingRepository,
        agente_facial_repository=None
    ):
        self.repository = repository
        self.embedding_service = embedding_service
        self.embedding_repository = embedding_repository
        self.agente_facial_repository = agente_facial_repository

    def criar(self, pessoa_id: uuid.UUID, arquivo):

        # 1. Verificar se a pessoa existe
        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        # 2. Validar extensão
        extensao = Path(arquivo.filename).suffix.lower()

        extensoes_permitidas = {
            ".jpg",
            ".jpeg",
            ".png"
        }

        if extensao not in extensoes_permitidas:
            raise ValueError(
                "Formato de imagem não permitido. "
                "Use JPG, JPEG ou PNG."
            )

        # 3. Ler o arquivo diretamente para memória
        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError("O arquivo enviado está vazio.")

        # 4. Criar nome único para identificar a foto
        nome_arquivo = f"{uuid.uuid4()}{extensao}"

        try:

            # 5. Criar registro da foto no banco
            foto = Foto(
                pessoa_id=pessoa_id,
                nome_arquivo=nome_arquivo,
                arquivo=conteudo
            )

            foto = self.repository.salvar(foto)

            # 6. Gerar embedding diretamente a partir dos bytes
            vetor = self.embedding_service.gerar_embedding(
                conteudo
            )

            # 7. Salvar embedding
            self.embedding_repository.salvar(
                foto_id=foto.id,
                vetor=vetor
            )

            # 8. Confirmar tudo
            self.repository.db.commit()

            return foto

        except Exception:

            # Desfazer alterações no banco
            self.repository.db.rollback()

            raise
        
    def criar_para_agente(
        self,
        agente_id: uuid.UUID,
        arquivo
    ):

        agente = (
            self.repository.db.query(Agente)
            .filter(Agente.id == agente_id)
            .first()
        )

        if not agente:
            raise ValueError(
                "Agente não encontrado."
            )

        if self.agente_facial_repository.buscar_por_agente_id(
            agente_id
        ):
            raise ValueError(
                "Este agente já possui um cadastro facial."
            )

        extensao = Path(
            arquivo.filename
        ).suffix.lower()

        extensoes_permitidas = {
            ".jpg",
            ".jpeg",
            ".png"
        }

        if extensao not in extensoes_permitidas:
            raise ValueError(
                "Formato de imagem não permitido. "
                "Use JPG, JPEG ou PNG."
            )

        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError(
                "O arquivo enviado está vazio."
            )

        nome_arquivo = (
            f"{uuid.uuid4()}{extensao}"
        )

        try:

            foto = Foto(
                agente_id=agente_id,
                nome_arquivo=nome_arquivo,
                arquivo=conteudo
            )

            foto = self.repository.salvar(foto)

            vetor = (
                self.embedding_service.gerar_embedding(
                    conteudo
                )
            )

            agente_facial = AgenteFacial(
                agente_id=agente_id,
                vetor=vetor
            )

            self.agente_facial_repository.salvar(
                agente_facial
            )

            self.repository.db.commit()

            return foto

        except Exception:

            self.repository.db.rollback()

            raise    

    def listar(self):

        return self.repository.listar()

    def buscar_por_id(self, id):

        foto = self.repository.buscar_por_id(id)

        if not foto:
            raise ValueError("Foto não encontrada.")

        return foto

    def listar_por_pessoa(self, pessoa_id):

        return self.repository.buscar_por_pessoa(
            pessoa_id
        )

    def deletar(self, id):

        foto = self.repository.buscar_por_id(id)

        if not foto:
            raise ValueError("Foto não encontrada.")

        self.repository.deletar(foto)