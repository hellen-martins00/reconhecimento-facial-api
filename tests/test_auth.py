
import uuid
from datetime import datetime, timedelta, timezone
from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from fastapi import HTTPException
from starlette.datastructures import UploadFile
from fastapi.security import HTTPAuthorizationCredentials

from jose import jwt

from app.auth.dependencies import (
    get_agente_atual,
    get_admin_atual
)

from app.auth.facial_service import LoginFacialService

from app.auth.security import (
    SECRET_KEY,
    ALGORITHM
)

from app.auth.schema import LoginRequest

from app.auth import router


# ==========================================================
# DEPENDENCIES - AUTENTICAÇÃO E AUTORIZAÇÃO
# ==========================================================

class TestAuthDependencies:

    @pytest.fixture
    def db(self):
        return MagicMock()

    def criar_token(self, payload):
        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    def criar_credentials(self, token):
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=token
        )

    @patch("app.auth.dependencies.AgenteRepository")
    def test_obter_agente_atual_com_token_valido(
        self, mock_repository, db
    ):

        agente_id = uuid.uuid4()

        token = self.criar_token({
            "sub": str(agente_id)
        })

        agente_mock = MagicMock()
        mock_repository.return_value.buscar_por_id.return_value = (
            agente_mock
        )

        resultado = get_agente_atual(
            credentials=self.criar_credentials(token),
            db=db
        )

        mock_repository.assert_called_once_with(db)

        mock_repository.return_value.buscar_por_id.assert_called_once_with(
            agente_id
        )

        assert resultado is agente_mock

    def test_token_invalido(self, db):

        credentials = self.criar_credentials(
            "token_invalido"
        )

        with pytest.raises(HTTPException) as exc:

            get_agente_atual(
                credentials=credentials,
                db=db
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token inválido ou expirado."

    def test_token_expirado(self, db):

        token = self.criar_token({
            "sub": str(uuid.uuid4()),
            "exp": datetime.now(timezone.utc) - timedelta(minutes=5)
        })

        with pytest.raises(HTTPException) as exc:

            get_agente_atual(
                credentials=self.criar_credentials(token),
                db=db
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token inválido ou expirado."

    def test_token_sem_sub(self, db):

        token = self.criar_token({
            "perfil": "ADMIN"
        })

        with pytest.raises(HTTPException) as exc:

            get_agente_atual(
                credentials=self.criar_credentials(token),
                db=db
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Token inválido."

    @patch("app.auth.dependencies.AgenteRepository")
    def test_agente_nao_encontrado(
        self, mock_repository, db
    ):

        agente_id = uuid.uuid4()

        token = self.criar_token({
            "sub": str(agente_id)
        })

        mock_repository.return_value.buscar_por_id.return_value = None

        with pytest.raises(HTTPException) as exc:

            get_agente_atual(
                credentials=self.criar_credentials(token),
                db=db
            )

        assert exc.value.status_code == 401
        assert exc.value.detail == "Agente não encontrado."

    def test_admin_com_perfil_admin(self):

        agente = MagicMock()
        agente.perfil = "ADMIN"

        resultado = get_admin_atual(agente)

        assert resultado is agente

    def test_agente_sem_permissao_de_admin(self):

        agente = MagicMock()
        agente.perfil = "AGENTE"

        with pytest.raises(HTTPException) as exc:

            get_admin_atual(agente)

        assert exc.value.status_code == 403

        assert exc.value.detail == (
            "Acesso permitido somente para administradores."
        )


# ==========================================================
# FACIAL SERVICE - LOGIN POR RECONHECIMENTO FACIAL
# ==========================================================

class TestLoginFacialService:

    @pytest.fixture
    def repository(self):
        return MagicMock()

    @pytest.fixture
    def service(self, repository):

        service = LoginFacialService.__new__(
            LoginFacialService
        )

        service.repository = repository
        service.embedding_service = MagicMock()

        return service

    def test_inicializar_servico(self, repository):

        with patch(
            "app.auth.facial_service.EmbeddingService"
        ) as mock_embedding:

            service = LoginFacialService(repository)

            assert service.repository is repository

            mock_embedding.assert_called_once()

            assert service.embedding_service is mock_embedding.return_value

    @patch("app.auth.facial_service.criar_token_acesso")
    def test_autenticacao_facial_com_sucesso(
        self, mock_token, service, repository
    ):

        vetor = [0.1] * 512

        agente_id = uuid.uuid4()

        agente = MagicMock()
        agente.id = agente_id

        agente_facial = MagicMock()
        agente_facial.agente = agente

        service.embedding_service.gerar_embedding.return_value = vetor

        repository.buscar_mais_semelhante.return_value = (
            agente_facial,
            0.3
        )

        mock_token.return_value = "token_gerado"

        resultado = service.autenticar(b"imagem")

        service.embedding_service.gerar_embedding.assert_called_once_with(
            b"imagem"
        )

        repository.buscar_mais_semelhante.assert_called_once_with(
            vetor
        )

        mock_token.assert_called_once_with(
            str(agente_id)
        )

        assert resultado["autenticado"] is True
        assert resultado["distancia"] == 0.3
        assert resultado["agente"] is agente
        assert resultado["access_token"] == "token_gerado"

    def test_nenhum_agente_facial_cadastrado(
        self, service, repository
    ):

        vetor = [0.2] * 512

        service.embedding_service.gerar_embedding.return_value = vetor

        repository.buscar_mais_semelhante.return_value = None

        resultado = service.autenticar(b"imagem")

        assert resultado == {
            "autenticado": False,
            "distancia": None,
            "agente": None,
            "access_token": None
        }

    def test_distancia_acima_do_limite(
        self, service, repository
    ):

        vetor = [0.2] * 512

        agente_facial = MagicMock()

        service.embedding_service.gerar_embedding.return_value = vetor

        repository.buscar_mais_semelhante.return_value = (
            agente_facial,
            0.8
        )

        with patch(
            "app.auth.facial_service.criar_token_acesso"
        ) as mock_token:

            resultado = service.autenticar(b"imagem")

        assert resultado == {
            "autenticado": False,
            "distancia": 0.8,
            "agente": None,
            "access_token": None
        }

        mock_token.assert_not_called()

    @patch("app.auth.facial_service.criar_token_acesso")
    def test_distancia_igual_ao_limite(
        self, mock_token, service, repository
    ):

        agente = MagicMock()
        agente.id = uuid.uuid4()

        agente_facial = MagicMock()
        agente_facial.agente = agente

        service.embedding_service.gerar_embedding.return_value = (
            [0.1] * 512
        )

        repository.buscar_mais_semelhante.return_value = (
            agente_facial,
            0.5
        )

        mock_token.return_value = "token_valido"

        resultado = service.autenticar(b"imagem")

        assert resultado["autenticado"] is True
        assert resultado["distancia"] == 0.5
        assert resultado["agente"] is agente
        assert resultado["access_token"] == "token_valido"

    @patch("app.auth.facial_service.criar_token_acesso")
    def test_converter_distancia_para_float(
        self, mock_token, service, repository
    ):

        agente = MagicMock()
        agente.id = uuid.uuid4()

        agente_facial = MagicMock()
        agente_facial.agente = agente

        service.embedding_service.gerar_embedding.return_value = (
            [0.1] * 512
        )

        repository.buscar_mais_semelhante.return_value = (
            agente_facial,
            "0.25"
        )

        mock_token.return_value = "token"

        resultado = service.autenticar(b"imagem")

        assert resultado["distancia"] == 0.25
        assert isinstance(resultado["distancia"], float)

    def test_propagacao_de_erro_na_geracao_embedding(
        self, service, repository
    ):

        service.embedding_service.gerar_embedding.side_effect = (
            ValueError("Nenhum rosto foi detectado na imagem.")
        )

        with pytest.raises(
            ValueError,
            match="Nenhum rosto foi detectado na imagem."
        ):

            service.autenticar(b"imagem")

        repository.buscar_mais_semelhante.assert_not_called()


# ==========================================================
# ROUTER - LOGIN COM USUARIO E SENHA
# ==========================================================

class TestLoginRouter:

    @pytest.fixture
    def db(self):
        return MagicMock()

    def test_login_com_sucesso(self, db):

        dados = LoginRequest(
            usuario="agente01",
            senha="senha123"
        )

        resposta_esperada = {
            "access_token": "token_valido",
            "token_type": "bearer",
            "id": uuid.uuid4(),
            "nome": "Agente Teste",
            "usuario": "agente01",
            "perfil": "AGENTE"
        }

        with patch(
            "app.auth.router.AgenteRepository"
        ) as mock_repository, patch(
            "app.auth.router.AuthService"
        ) as mock_service:

            mock_service.return_value.login.return_value = (
                resposta_esperada
            )

            resultado = router.login(dados, db)

        mock_repository.assert_called_once_with(db)

        mock_service.assert_called_once_with(
            mock_repository.return_value
        )

        mock_service.return_value.login.assert_called_once_with(
            "agente01",
            "senha123"
        )

        assert resultado == resposta_esperada

    def test_login_com_credenciais_invalidas(self, db):

        dados = LoginRequest(
            usuario="agente01",
            senha="senha_errada"
        )

        with patch(
            "app.auth.router.AgenteRepository"
        ), patch(
            "app.auth.router.AuthService"
        ) as mock_service:

            mock_service.return_value.login.side_effect = (
                ValueError("Usuário ou senha inválidos.")
            )

            with pytest.raises(HTTPException) as exc:

                router.login(dados, db)

        assert exc.value.status_code == 401
        assert exc.value.detail == "Usuário ou senha inválidos."


# ==========================================================
# ROUTER - LOGIN FACIAL
# ==========================================================

class TestLoginFacialRouter:

    @pytest.fixture
    def db(self):
        return MagicMock()

    def criar_upload(self, nome="foto.jpg", conteudo=b"imagem"):

        return UploadFile(
            filename=nome,
            file=BytesIO(conteudo)
        )

    def test_login_facial_extensao_nao_permitida(self, db):

        arquivo = self.criar_upload("foto.gif")

        with pytest.raises(HTTPException) as exc:

            router.login_facial(arquivo, db)

        assert exc.value.status_code == 400

        assert exc.value.detail == (
            "Formato de imagem não permitido. Use JPG, JPEG ou PNG."
        )

    def test_login_facial_arquivo_vazio(self, db):

        arquivo = self.criar_upload(
            "foto.jpg",
            b""
        )

        with pytest.raises(HTTPException) as exc:

            router.login_facial(arquivo, db)

        assert exc.value.status_code == 400
        assert exc.value.detail == "O arquivo enviado está vazio."

    def test_login_facial_nao_reconhecido(self, db):

        arquivo = self.criar_upload()

        resultado_esperado = {
            "autenticado": False,
            "distancia": 0.8,
            "agente": None,
            "access_token": None
        }

        with patch(
            "app.auth.router.AgenteFacialRepository"
        ) as mock_repository, patch(
            "app.auth.router.LoginFacialService"
        ) as mock_service:

            mock_service.return_value.autenticar.return_value = (
                resultado_esperado
            )

            resultado = router.login_facial(arquivo, db)

        mock_repository.assert_called_once_with(db)

        mock_service.assert_called_once_with(
            mock_repository.return_value
        )

        assert resultado == {
            "autenticado": False,
            "distancia": 0.8,
            "access_token": None,
            "token_type": None,
            "id": None,
            "nome": None,
            "usuario": None,
            "perfil": None
        }

    def test_login_facial_reconhecido(self, db):

        arquivo = self.criar_upload("foto.PNG")

        agente = MagicMock()
        agente.id = uuid.uuid4()
        agente.nome = "Agente Teste"
        agente.usuario = "agente01"
        agente.perfil = "ADMIN"

        resultado_esperado = {
            "autenticado": True,
            "distancia": 0.25,
            "agente": agente,
            "access_token": "token_valido"
        }

        with patch(
            "app.auth.router.AgenteFacialRepository"
        ) as mock_repository, patch(
            "app.auth.router.LoginFacialService"
        ) as mock_service:

            mock_service.return_value.autenticar.return_value = (
                resultado_esperado
            )

            resultado = router.login_facial(arquivo, db)

        assert resultado == {
            "autenticado": True,
            "distancia": 0.25,
            "access_token": "token_valido",
            "token_type": "bearer",
            "id": agente.id,
            "nome": agente.nome,
            "usuario": agente.usuario,
            "perfil": agente.perfil
        }

    def test_login_facial_erro_no_processamento(self, db):

        arquivo = self.criar_upload()

        with patch(
            "app.auth.router.AgenteFacialRepository"
        ), patch(
            "app.auth.router.LoginFacialService"
        ) as mock_service:

            mock_service.return_value.autenticar.side_effect = (
                ValueError("Nenhum rosto foi detectado na imagem.")
            )

            with pytest.raises(HTTPException) as exc:

                router.login_facial(arquivo, db)

        assert exc.value.status_code == 400

        assert exc.value.detail == (
            "Nenhum rosto foi detectado na imagem."
        )
