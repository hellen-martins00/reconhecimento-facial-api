
import uuid
from datetime import datetime
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from fastapi import HTTPException, UploadFile

from app.agentes.model import Agente
from app.agentes.repository import AgenteRepository
from app.agentes.schema import AgenteCreate, AgenteUpdate
from app.agentes.service import AgenteService
from app.agentes import router as agentes_router


# ==========================================================
# REPOSITORY
# ==========================================================

class TestAgenteRepository:

    @pytest.fixture
    def db(self):
        return MagicMock()

    @pytest.fixture
    def repository(self, db):
        return AgenteRepository(db)

    @pytest.fixture
    def agente(self):
        return Agente(
            nome="Agente Teste",
            usuario="agente01",
            senha_hash="hash_teste",
            perfil="AGENTE"
        )

    def test_inicializar_repository(self, db):

        repository = AgenteRepository(db)

        assert repository.db is db

    def test_salvar_agente(
        self, repository, db, agente
    ):

        resultado = repository.salvar(agente)

        db.add.assert_called_once_with(agente)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(agente)

        assert resultado is agente

    def test_buscar_por_usuario_encontrado(
        self, repository, db, agente
    ):

        db.query.return_value.filter.return_value.first.return_value = (
            agente
        )

        resultado = repository.buscar_por_usuario(
            "agente01"
        )

        db.query.assert_called_once_with(Agente)
        db.query.return_value.filter.assert_called_once()

        assert resultado is agente

    def test_buscar_por_usuario_nao_encontrado(
        self, repository, db
    ):

        db.query.return_value.filter.return_value.first.return_value = None

        resultado = repository.buscar_por_usuario(
            "inexistente"
        )

        assert resultado is None

    def test_buscar_por_id_encontrado(
        self, repository, db, agente
    ):

        agente_id = uuid.uuid4()

        db.query.return_value.filter.return_value.first.return_value = (
            agente
        )

        resultado = repository.buscar_por_id(agente_id)

        db.query.assert_called_once_with(Agente)
        db.query.return_value.filter.assert_called_once()

        assert resultado is agente

    def test_buscar_por_id_nao_encontrado(
        self, repository, db
    ):

        agente_id = uuid.uuid4()

        db.query.return_value.filter.return_value.first.return_value = None

        resultado = repository.buscar_por_id(agente_id)

        assert resultado is None

    def test_listar_agentes(
        self, repository, db, agente
    ):

        agentes = [agente, agente]

        db.query.return_value.all.return_value = agentes

        resultado = repository.listar()

        db.query.assert_called_once_with(Agente)
        db.query.return_value.all.assert_called_once()

        assert resultado == agentes

    def test_listar_sem_agentes(
        self, repository, db
    ):

        db.query.return_value.all.return_value = []

        resultado = repository.listar()

        assert resultado == []

    def test_atualizar_agente(
        self, repository, db, agente
    ):

        resultado = repository.atualizar(agente)

        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(agente)

        assert resultado is agente

    def test_deletar_agente(
        self, repository, db, agente
    ):

        resultado = repository.deletar(agente)

        db.delete.assert_called_once_with(agente)
        db.commit.assert_called_once()

        assert resultado is None


# ==========================================================
# SERVICE
# ==========================================================

class TestAgenteService:

    @pytest.fixture
    def repository(self):
        return MagicMock()

    @pytest.fixture
    def service(self, repository):
        return AgenteService(repository)

    @pytest.fixture
    def dados_criacao(self):
        return AgenteCreate(
            nome="Agente Teste",
            usuario="agente01",
            senha="senha123",
            perfil="AGENTE"
        )

    @pytest.fixture
    def agente(self):
        return Agente(
            nome="Agente Teste",
            usuario="agente01",
            senha_hash="hash_antigo",
            perfil="AGENTE"
        )

    def test_inicializar_service(
        self, repository
    ):

        service = AgenteService(repository)

        assert service.repository is repository

    def test_criar_agente_com_sucesso(
        self,
        service,
        repository,
        dados_criacao
    ):

        repository.buscar_por_usuario.return_value = None

        agente_salvo = MagicMock()

        repository.salvar.return_value = agente_salvo

        with patch(
            "app.agentes.service.pwd_context.hash",
            return_value="senha_hash_gerada"
        ) as mock_hash:

            resultado = service.criar(dados_criacao)

        repository.buscar_por_usuario.assert_called_once_with(
            "agente01"
        )

        mock_hash.assert_called_once_with("senha123")

        repository.salvar.assert_called_once()

        agente_criado = repository.salvar.call_args[0][0]

        assert agente_criado.nome == "Agente Teste"
        assert agente_criado.usuario == "agente01"
        assert agente_criado.senha_hash == "senha_hash_gerada"
        assert agente_criado.perfil == "AGENTE"

        assert resultado is agente_salvo

    def test_criar_agente_com_usuario_existente(
        self,
        service,
        repository,
        dados_criacao
    ):

        repository.buscar_por_usuario.return_value = MagicMock()

        with patch(
            "app.agentes.service.pwd_context.hash"
        ) as mock_hash:

            with pytest.raises(
                ValueError,
                match="Já existe um agente cadastrado com este usuário."
            ):

                service.criar(dados_criacao)

        mock_hash.assert_not_called()
        repository.salvar.assert_not_called()

    def test_listar_agentes(
        self, service, repository, agente
    ):

        agentes = [agente]

        repository.listar.return_value = agentes

        resultado = service.listar()

        repository.listar.assert_called_once()

        assert resultado == agentes

    def test_listar_sem_agentes(
        self, service, repository
    ):

        repository.listar.return_value = []

        resultado = service.listar()

        assert resultado == []

    def test_buscar_por_id(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente

        resultado = service.buscar_por_id(agente_id)

        repository.buscar_por_id.assert_called_once_with(
            agente_id
        )

        assert resultado is agente

    def test_buscar_por_id_inexistente(
        self, service, repository
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = None

        resultado = service.buscar_por_id(agente_id)

        assert resultado is None

    def test_atualizar_agente_inexistente(
        self, service, repository
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = None

        dados = AgenteUpdate(nome="Novo Nome")

        with pytest.raises(
            ValueError,
            match="Agente não encontrado."
        ):

            service.atualizar(agente_id, dados)

        repository.atualizar.assert_not_called()

    def test_atualizar_somente_nome(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente
        repository.atualizar.return_value = agente

        dados = AgenteUpdate(
            nome="Nome Atualizado"
        )

        resultado = service.atualizar(
            agente_id,
            dados
        )

        assert agente.nome == "Nome Atualizado"
        assert agente.usuario == "agente01"
        assert agente.senha_hash == "hash_antigo"

        repository.buscar_por_id.assert_called_once_with(
            agente_id
        )

        repository.atualizar.assert_called_once_with(agente)

        assert resultado is agente

    def test_atualizar_usuario_sem_duplicidade(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente
        repository.buscar_por_usuario.return_value = None
        repository.atualizar.return_value = agente

        dados = AgenteUpdate(
            usuario="novo_usuario"
        )

        resultado = service.atualizar(
            agente_id,
            dados
        )

        repository.buscar_por_usuario.assert_called_once_with(
            "novo_usuario"
        )

        assert agente.usuario == "novo_usuario"
        assert resultado is agente

    def test_atualizar_usuario_que_ja_pertence_ao_proprio_agente(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        agente.id = agente_id

        repository.buscar_por_id.return_value = agente

        # O usuário já existe, mas pertence ao próprio agente.
        repository.buscar_por_usuario.return_value = agente

        repository.atualizar.return_value = agente

        dados = AgenteUpdate(
            usuario="agente01"
        )

        resultado = service.atualizar(
            agente_id,
            dados
        )

        assert agente.usuario == "agente01"

        repository.atualizar.assert_called_once_with(
            agente
        )

        assert resultado is agente

    def test_atualizar_usuario_ja_utilizado_por_outro_agente(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        agente.id = agente_id

        outro_agente = MagicMock()
        outro_agente.id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente
        repository.buscar_por_usuario.return_value = outro_agente

        dados = AgenteUpdate(
            usuario="outro_usuario"
        )

        with pytest.raises(
            ValueError,
            match="Já existe um agente cadastrado com este usuário."
        ):

            service.atualizar(agente_id, dados)

        repository.atualizar.assert_not_called()

    def test_atualizar_senha(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente
        repository.atualizar.return_value = agente

        dados = AgenteUpdate(
            senha="nova_senha123"
        )

        with patch(
            "app.agentes.service.pwd_context.hash",
            return_value="novo_hash"
        ) as mock_hash:

            resultado = service.atualizar(
                agente_id,
                dados
            )

        mock_hash.assert_called_once_with(
            "nova_senha123"
        )

        assert agente.senha_hash == "novo_hash"
        assert resultado is agente

    def test_atualizar_sem_alteracoes(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente
        repository.atualizar.return_value = agente

        dados = AgenteUpdate()

        resultado = service.atualizar(
            agente_id,
            dados
        )

        assert agente.nome == "Agente Teste"
        assert agente.usuario == "agente01"
        assert agente.senha_hash == "hash_antigo"

        repository.buscar_por_usuario.assert_not_called()

        repository.atualizar.assert_called_once_with(
            agente
        )

        assert resultado is agente

    def test_deletar_agente_com_sucesso(
        self, service, repository, agente
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = agente

        resultado = service.deletar(agente_id)

        repository.buscar_por_id.assert_called_once_with(
            agente_id
        )

        repository.deletar.assert_called_once_with(
            agente
        )

        assert resultado is None

    def test_deletar_agente_inexistente(
        self, service, repository
    ):

        agente_id = uuid.uuid4()

        repository.buscar_por_id.return_value = None

        with pytest.raises(
            ValueError,
            match="Agente não encontrado."
        ):

            service.deletar(agente_id)

        repository.deletar.assert_not_called()


# ==========================================================
# ROUTER - CONFIGURAÇÕES AUXILIARES
# ==========================================================

class TestAgenteRouter:

    @pytest.fixture
    def db(self):
        return MagicMock()

    @pytest.fixture
    def admin(self):
        agente = MagicMock()
        agente.id = uuid.uuid4()
        agente.perfil = "ADMIN"
        return agente

    @pytest.fixture
    def agente_atual(self):
        agente = MagicMock()
        agente.id = uuid.uuid4()
        agente.perfil = "AGENTE"
        return agente

    @pytest.fixture
    def outro_agente(self):
        agente = MagicMock()
        agente.id = uuid.uuid4()
        agente.perfil = "AGENTE"
        return agente

    def criar_upload(
        self,
        nome="foto.jpg",
        conteudo=b"conteudo_imagem"
    ):

        return UploadFile(
            filename=nome,
            file=BytesIO(conteudo)
        )

    # ------------------------------------------------------
    # CRIAR AGENTE
    # ------------------------------------------------------

    def test_criar_agente_com_sucesso(
        self, db, admin
    ):

        dados = AgenteCreate(
            nome="Novo Agente",
            usuario="novo01",
            senha="senha123",
            perfil="AGENTE"
        )

        agente_criado = MagicMock()

        with patch(
            "app.agentes.router.AgenteRepository"
        ) as mock_repository, patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.criar.return_value = (
                agente_criado
            )

            resultado = agentes_router.criar_agente(
                dados,
                db,
                admin
            )

        mock_repository.assert_called_once_with(db)

        mock_service.assert_called_once_with(
            mock_repository.return_value
        )

        mock_service.return_value.criar.assert_called_once_with(
            dados
        )

        assert resultado is agente_criado

    def test_criar_agente_com_erro(
        self, db, admin
    ):

        dados = AgenteCreate(
            nome="Novo Agente",
            usuario="novo01",
            senha="senha123"
        )

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.criar.side_effect = (
                ValueError("Já existe um agente cadastrado com este usuário.")
            )

            with pytest.raises(HTTPException) as exc:

                agentes_router.criar_agente(
                    dados,
                    db,
                    admin
                )

        assert exc.value.status_code == 400

    # ------------------------------------------------------
    # LISTAR AGENTES
    # ------------------------------------------------------

    def test_listar_agentes(
        self, db, agente_atual
    ):

        agentes = [MagicMock(), MagicMock()]

        with patch(
            "app.agentes.router.AgenteRepository"
        ) as mock_repository, patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.listar.return_value = agentes

            resultado = agentes_router.listar_agentes(
                db,
                agente_atual
            )

        mock_repository.assert_called_once_with(db)

        mock_service.return_value.listar.assert_called_once()

        assert resultado == agentes

    # ------------------------------------------------------
    # BUSCAR AGENTE
    # ------------------------------------------------------

    def test_buscar_agente_encontrado(
        self, db, agente_atual
    ):

        agente_id = uuid.uuid4()
        agente = MagicMock()

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.buscar_por_id.return_value = (
                agente
            )

            resultado = agentes_router.buscar_agente(
                agente_id,
                db,
                agente_atual
            )

        mock_service.return_value.buscar_por_id.assert_called_once_with(
            agente_id
        )

        assert resultado is agente

    def test_buscar_agente_nao_encontrado(
        self, db, agente_atual
    ):

        agente_id = uuid.uuid4()

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.buscar_por_id.return_value = None

            with pytest.raises(HTTPException) as exc:

                agentes_router.buscar_agente(
                    agente_id,
                    db,
                    agente_atual
                )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Agente não encontrado."

    # ------------------------------------------------------
    # ATUALIZAR AGENTE
    # ------------------------------------------------------

    def test_atualizar_proprios_dados(
        self, db, agente_atual
    ):

        dados = AgenteUpdate(
            nome="Nome Atualizado"
        )

        agente_id = agente_atual.id

        agente_atualizado = MagicMock()

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.atualizar.return_value = (
                agente_atualizado
            )

            resultado = agentes_router.atualizar_agente(
                agente_id,
                dados,
                db,
                agente_atual
            )

        mock_service.return_value.atualizar.assert_called_once_with(
            agente_id,
            dados
        )

        assert resultado is agente_atualizado

    def test_admin_pode_atualizar_outro_agente(
        self, db, admin
    ):

        agente_id = uuid.uuid4()

        dados = AgenteUpdate(
            nome="Nome Alterado"
        )

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.atualizar.return_value = (
                MagicMock()
            )

            resultado = agentes_router.atualizar_agente(
                agente_id,
                dados,
                db,
                admin
            )

        mock_service.return_value.atualizar.assert_called_once_with(
            agente_id,
            dados
        )

        assert resultado is not None

    def test_agente_nao_pode_atualizar_outro(
        self, db, agente_atual, outro_agente
    ):

        dados = AgenteUpdate(
            nome="Nome Alterado"
        )

        with patch(
            "app.agentes.router.AgenteRepository"
        ) as mock_repository:

            with pytest.raises(HTTPException) as exc:

                agentes_router.atualizar_agente(
                    outro_agente.id,
                    dados,
                    db,
                    agente_atual
                )

        assert exc.value.status_code == 403

        assert exc.value.detail == (
            "Você só pode editar seus próprios dados."
        )

        mock_repository.assert_not_called()

    def test_atualizar_agente_com_erro_de_validacao(
        self, db, agente_atual
    ):

        dados = AgenteUpdate(
            nome="Nome Alterado"
        )

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.atualizar.side_effect = (
                ValueError("Agente não encontrado.")
            )

            with pytest.raises(HTTPException) as exc:

                agentes_router.atualizar_agente(
                    agente_atual.id,
                    dados,
                    db,
                    agente_atual
                )

        assert exc.value.status_code == 400

    # ------------------------------------------------------
    # CADASTRAR FOTO FACIAL
    # ------------------------------------------------------

    def test_cadastrar_foto_propria(
        self, db, agente_atual
    ):

        arquivo = self.criar_upload()

        foto_criada = MagicMock()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.criar_para_agente.return_value = (
                foto_criada
            )

            resultado = agentes_router.cadastrar_foto_facial(
                agente_atual.id,
                arquivo,
                db,
                agente_atual
            )

        mock_service.return_value.criar_para_agente.assert_called_once_with(
            agente_atual.id,
            arquivo
        )

        assert resultado is foto_criada

    def test_admin_cadastra_foto_de_outro_agente(
        self, db, admin, outro_agente
    ):

        arquivo = self.criar_upload()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.criar_para_agente.return_value = (
                MagicMock()
            )

            resultado = agentes_router.cadastrar_foto_facial(
                outro_agente.id,
                arquivo,
                db,
                admin
            )

        assert resultado is not None

        mock_service.return_value.criar_para_agente.assert_called_once_with(
            outro_agente.id,
            arquivo
        )

    def test_agente_nao_pode_cadastrar_foto_de_outro(
        self, db, agente_atual, outro_agente
    ):

        arquivo = self.criar_upload()

        with pytest.raises(HTTPException) as exc:

            agentes_router.cadastrar_foto_facial(
                outro_agente.id,
                arquivo,
                db,
                agente_atual
            )

        assert exc.value.status_code == 403

        assert exc.value.detail == (
            "Você só pode cadastrar sua própria foto facial."
        )

    def test_cadastrar_foto_com_erro(
        self, db, agente_atual
    ):

        arquivo = self.criar_upload()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.criar_para_agente.side_effect = (
                ValueError("Erro ao processar imagem.")
            )

            with pytest.raises(HTTPException) as exc:

                agentes_router.cadastrar_foto_facial(
                    agente_atual.id,
                    arquivo,
                    db,
                    agente_atual
                )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Erro ao processar imagem."

    # ------------------------------------------------------
    # ATUALIZAR FOTO FACIAL
    # ------------------------------------------------------

    def test_atualizar_foto_propria(
        self, db, agente_atual
    ):

        arquivo = self.criar_upload()

        foto_atualizada = MagicMock()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.atualizar_foto_agente.return_value = (
                foto_atualizada
            )

            resultado = agentes_router.atualizar_foto_facial(
                agente_atual.id,
                arquivo,
                db,
                agente_atual
            )

        mock_service.return_value.atualizar_foto_agente.assert_called_once_with(
            agente_atual.id,
            arquivo
        )

        assert resultado is foto_atualizada

    def test_admin_atualiza_foto_de_outro(
        self, db, admin, outro_agente
    ):

        arquivo = self.criar_upload()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.atualizar_foto_agente.return_value = (
                MagicMock()
            )

            resultado = agentes_router.atualizar_foto_facial(
                outro_agente.id,
                arquivo,
                db,
                admin
            )

        assert resultado is not None

    def test_agente_nao_pode_atualizar_foto_de_outro(
        self, db, agente_atual, outro_agente
    ):

        arquivo = self.criar_upload()

        with pytest.raises(HTTPException) as exc:

            agentes_router.atualizar_foto_facial(
                outro_agente.id,
                arquivo,
                db,
                agente_atual
            )

        assert exc.value.status_code == 403

        assert exc.value.detail == (
            "Você só pode atualizar sua própria foto facial."
        )

    def test_atualizar_foto_com_erro(
        self, db, agente_atual
    ):

        arquivo = self.criar_upload()

        with patch(
            "app.agentes.router.FotoRepository"
        ), patch(
            "app.agentes.router.EmbeddingRepository"
        ), patch(
            "app.agentes.router.AgenteFacialRepository"
        ), patch(
            "app.agentes.router.EmbeddingService"
        ), patch(
            "app.agentes.router.FotoService"
        ) as mock_service:

            mock_service.return_value.atualizar_foto_agente.side_effect = (
                ValueError("Erro ao atualizar foto.")
            )

            with pytest.raises(HTTPException) as exc:

                agentes_router.atualizar_foto_facial(
                    agente_atual.id,
                    arquivo,
                    db,
                    agente_atual
                )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Erro ao atualizar foto."

    # ------------------------------------------------------
    # CARREGAR FOTO
    # ------------------------------------------------------

    def test_carregar_foto_sem_foto(
        self, db, agente_atual
    ):

        agente_id = uuid.uuid4()

        with patch(
            "app.agentes.router.FotoRepository"
        ) as mock_repository:

            mock_repository.return_value.buscar_mais_recente_por_agente.return_value = (
                None
            )

            resultado = agentes_router.carregar_foto_agente(
                agente_id,
                db,
                agente_atual
            )

        assert resultado.status_code == 204

    @pytest.mark.parametrize(
        "nome, media_type",
        [
            ("foto.jpg", "image/jpeg"),
            ("foto.jpeg", "image/jpeg"),
            ("foto.png", "image/png"),
            ("foto.webp", "application/octet-stream"),
            ("foto", "application/octet-stream")
        ]
    )
    def test_carregar_foto_com_diferentes_extensoes(
        self, db, agente_atual, nome, media_type
    ):

        agente_id = uuid.uuid4()

        foto = MagicMock()
        foto.nome_arquivo = nome
        foto.arquivo = b"conteudo_da_foto"

        with patch(
            "app.agentes.router.FotoRepository"
        ) as mock_repository:

            mock_repository.return_value.buscar_mais_recente_por_agente.return_value = (
                foto
            )

            resultado = agentes_router.carregar_foto_agente(
                agente_id,
                db,
                agente_atual
            )

        assert resultado.status_code == 200
        assert resultado.media_type == media_type
        assert resultado.body == b"conteudo_da_foto"

        mock_repository.return_value.buscar_mais_recente_por_agente.assert_called_once_with(
            agente_id
        )

    # ------------------------------------------------------
    # EXCLUIR AGENTE
    # ------------------------------------------------------

    def test_deletar_agente_com_sucesso(
        self, db, admin
    ):

        agente_id = uuid.uuid4()

        with patch(
            "app.agentes.router.AgenteRepository"
        ) as mock_repository, patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            resultado = agentes_router.deletar_agente(
                agente_id,
                db,
                admin
            )

        mock_repository.assert_called_once_with(db)

        mock_service.assert_called_once_with(
            mock_repository.return_value
        )

        mock_service.return_value.deletar.assert_called_once_with(
            agente_id
        )

        assert resultado is None

    def test_deletar_agente_inexistente(
        self, db, admin
    ):

        agente_id = uuid.uuid4()

        with patch(
            "app.agentes.router.AgenteRepository"
        ), patch(
            "app.agentes.router.AgenteService"
        ) as mock_service:

            mock_service.return_value.deletar.side_effect = (
                ValueError("Agente não encontrado.")
            )

            with pytest.raises(HTTPException) as exc:

                agentes_router.deletar_agente(
                    agente_id,
                    db,
                    admin
                )

        assert exc.value.status_code == 404
        assert exc.value.detail == "Agente não encontrado."
