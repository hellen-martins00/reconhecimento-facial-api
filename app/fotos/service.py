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

    # CRIAR FOTO DE UMA PESSOA
    def criar(
        self,
        pessoa_id: uuid.UUID,
        arquivo
    ):

        # Verificar se a pessoa existe
        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError(
                "Pessoa não encontrada."
            )

        # Validar extensão
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

        # Ler arquivo
        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError(
                "O arquivo enviado está vazio."
            )

        # Criar nome único
        nome_arquivo = (
            f"{uuid.uuid4()}{extensao}"
        )

        try:

            # Criar registro da foto
            foto = Foto(
                pessoa_id=pessoa_id,
                nome_arquivo=nome_arquivo,
                arquivo=conteudo
            )

            foto = self.repository.salvar(
                foto
            )

            # Gerar embedding
            vetor = (
                self.embedding_service
                .gerar_embedding(conteudo)
            )

            # Salvar embedding
            self.embedding_repository.salvar(
                foto_id=foto.id,
                vetor=vetor
            )

            # Confirmar alterações
            self.repository.db.commit()

            return foto

        except Exception:

            self.repository.db.rollback()

            raise

    # CRIAR FOTO FACIAL DE UM AGENTE
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

        # Verificar se já possui cadastro facial
        agente_facial = (
            self.agente_facial_repository
            .buscar_por_agente_id(agente_id)
        )

        if agente_facial:
            raise ValueError(
                "Este agente já possui um cadastro facial."
            )

        # Validar extensão
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

        # Ler arquivo
        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError(
                "O arquivo enviado está vazio."
            )

        # Criar nome único
        nome_arquivo = (
            f"{uuid.uuid4()}{extensao}"
        )

        try:

            # Criar foto do agente
            foto = Foto(
                agente_id=agente_id,
                nome_arquivo=nome_arquivo,
                arquivo=conteudo
            )

            foto = self.repository.salvar(
                foto
            )

            # Gerar embedding facial
            vetor = (
                self.embedding_service
                .gerar_embedding(conteudo)
            )

            # Criar cadastro facial
            agente_facial = AgenteFacial(
                agente_id=agente_id,
                vetor=vetor
            )

            self.agente_facial_repository.salvar(
                agente_facial
            )

            # Confirmar alterações
            self.repository.db.commit()

            return foto

        except Exception:

            self.repository.db.rollback()

            raise

    # ATUALIZAR FOTO FACIAL DO AGENTE
    def atualizar_foto_agente(
        self,
        agente_id: uuid.UUID,
        arquivo
    ):

        # Verificar se o agente existe
        agente = (
            self.repository.db.query(Agente)
            .filter(Agente.id == agente_id)
            .first()
        )

        if not agente:
            raise ValueError(
                "Agente não encontrado."
            )

        # Localizar cadastro facial
        agente_facial = (
            self.agente_facial_repository
            .buscar_por_agente_id(agente_id)
        )

        if not agente_facial:
            raise ValueError(
                "Este agente ainda não possui cadastro facial."
            )

        # Validar extensão
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

        # Ler arquivo
        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError(
                "O arquivo enviado está vazio."
            )

        try:

            # Gerar novo embedding
            vetor = (
                self.embedding_service
                .gerar_embedding(conteudo)
            )

            # Localizar foto atual do agente
            foto = (
                self.repository.db.query(Foto)
                .filter(
                    Foto.agente_id == agente_id
                )
                .first()
            )

            if not foto:
                raise ValueError(
                    "Foto facial do agente não encontrada."
                )

            # Atualizar nome do arquivo
            foto.nome_arquivo = (
                f"{uuid.uuid4()}{extensao}"
            )

            # Atualizar imagem
            foto.arquivo = conteudo

            # Atualizar embedding
            agente_facial.vetor = vetor

            # Salvar alterações
            self.repository.db.commit()

            self.repository.db.refresh(
                foto
            )

            return foto

        except Exception:

            self.repository.db.rollback()

            raise

    # LISTAR FOTOS
    def listar(self):

        return self.repository.listar()

    # BUSCAR FOTO POR ID
    def buscar_por_id(
        self,
        id
    ):

        foto = (
            self.repository.buscar_por_id(id)
        )

        if not foto:
            raise ValueError(
                "Foto não encontrada."
            )

        return foto

    # LISTAR FOTOS DE UMA PESSOA
    def listar_por_pessoa(
        self,
        pessoa_id
    ):

        return self.repository.buscar_por_pessoa(
            pessoa_id
        )

    # DELETAR FOTO
    def deletar(
        self,
        id
    ):

        foto = (
            self.repository.buscar_por_id(id)
        )

        if not foto:
            raise ValueError(
                "Foto não encontrada."
            )

        self.repository.deletar(
            foto
        )
        
    def atualizar_foto_pessoa(
        self,
        foto_id: uuid.UUID,
        arquivo
    ):

        # 1. Buscar a foto existente
        foto = self.repository.buscar_por_id(foto_id)

        if not foto:
            raise ValueError(
                "Foto não encontrada."
            )

        # 2. Garantir que a foto pertence a uma pessoa
        if not foto.pessoa_id:
            raise ValueError(
                "Esta foto não pertence a uma pessoa."
            )

        # 3. Verificar se a pessoa existe
        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(
                Pessoa.id == foto.pessoa_id
            )
            .first()
        )

        if not pessoa:
            raise ValueError(
                "Pessoa não encontrada."
            )

        # 4. Validar extensão
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

        # 5. Ler o novo arquivo
        conteudo = arquivo.file.read()

        if not conteudo:
            raise ValueError(
                "O arquivo enviado está vazio."
            )

        try:

            # 6. Gerar novo embedding
            vetor = (
                self.embedding_service
                .gerar_embedding(conteudo)
            )

            # 7. Atualizar os dados da foto
            foto.nome_arquivo = (
                f"{uuid.uuid4()}{extensao}"
            )

            foto.arquivo = conteudo

            # 8. Buscar o embedding atual da foto
            embedding = (
                self.embedding_repository
                .buscar_por_foto_id(foto_id)
            )

            if not embedding:
                raise ValueError(
                    "Embedding facial da foto não encontrado."
                )

            # 9. Atualizar o embedding
            embedding.vetor = vetor

            # 10. Confirmar alterações
            self.repository.db.commit()

            # 11. Atualizar objeto
            self.repository.db.refresh(foto)

            return foto

        except Exception:

            self.repository.db.rollback()

            raise