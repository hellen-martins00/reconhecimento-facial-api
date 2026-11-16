
import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import cv2
import numpy as np
import pytest

from app.embeddings.model import EmbeddingFacial
from app.embeddings.repository import EmbeddingRepository
from app.embeddings.schema import EmbeddingResponse
from app.embeddings.service import EmbeddingService


# ==========================================================
# MODEL
# ==========================================================

class TestEmbeddingModel:

    def test_estrutura_da_tabela(self):
        assert EmbeddingFacial.__tablename__ == "embeddings_faciais"

    def test_chave_primaria(self):
        coluna = EmbeddingFacial.__table__.columns["id"]

        assert coluna.primary_key is True

    def test_foto_id_obrigatorio(self):
        coluna = EmbeddingFacial.__table__.columns["foto_id"]

        assert coluna.nullable is False

    def test_vetor_obrigatorio_com_512_dimensoes(self):
        coluna = EmbeddingFacial.__table__.columns["vetor"]

        assert coluna.nullable is False
        assert coluna.type.dim == 512

    def test_relacionamento_com_foto(self):
        relacionamento = EmbeddingFacial.__mapper__.relationships["foto"]

        assert relacionamento.back_populates == "embeddings"

    def test_foreign_key_com_cascade(self):
        coluna = EmbeddingFacial.__table__.columns["foto_id"]
        foreign_key = next(iter(coluna.foreign_keys))

        assert foreign_key.target_fullname == "fotos.id"
        assert foreign_key.ondelete == "CASCADE"


# ==========================================================
# SCHEMA
# ==========================================================

class TestEmbeddingSchema:

    def test_validar_resposta_embedding(self):
        embedding_id = uuid.uuid4()
        foto_id = uuid.uuid4()
        agora = datetime.now()
        vetor = [0.1] * 512

        dados = SimpleNamespace(
            id=embedding_id,
            foto_id=foto_id,
            vetor=vetor,
            created_at=agora
        )

        resposta = EmbeddingResponse.model_validate(dados)

        assert resposta.id == embedding_id
        assert resposta.foto_id == foto_id
        assert resposta.vetor == vetor
        assert resposta.created_at == agora

    def test_converter_resposta_para_dict(self):
        embedding_id = uuid.uuid4()
        foto_id = uuid.uuid4()
        agora = datetime.now()
        vetor = [0.5] * 512

        dados = SimpleNamespace(
            id=embedding_id,
            foto_id=foto_id,
            vetor=vetor,
            created_at=agora
        )

        resposta = EmbeddingResponse.model_validate(dados)

        resultado = resposta.model_dump()

        assert resultado["id"] == embedding_id
        assert resultado["foto_id"] == foto_id
        assert resultado["vetor"] == vetor
        assert resultado["created_at"] == agora


# ==========================================================
# REPOSITORY
# ==========================================================

class TestEmbeddingRepository:

    @pytest.fixture
    def db(self):
        return MagicMock()

    @pytest.fixture
    def repository(self, db):
        return EmbeddingRepository(db)

    def test_inicializar_repository(self, db):
        repository = EmbeddingRepository(db)

        assert repository.db is db

    @patch("app.embeddings.repository.EmbeddingFacial")
    def test_salvar_embedding(self, mock_model, repository, db):

        foto_id = uuid.uuid4()
        vetor = [0.1] * 512

        embedding_mock = MagicMock()
        mock_model.return_value = embedding_mock

        resultado = repository.salvar(
            foto_id=foto_id,
            vetor=vetor
        )

        mock_model.assert_called_once_with(
            foto_id=foto_id,
            vetor=vetor
        )

        db.add.assert_called_once_with(embedding_mock)
        db.flush.assert_called_once()
        db.refresh.assert_called_once_with(embedding_mock)

        assert resultado is embedding_mock

    @patch("app.embeddings.repository.EmbeddingFacial")
    def test_buscar_por_foto_id_encontrado(
        self, mock_model, repository, db
    ):

        foto_id = uuid.uuid4()
        embedding_mock = MagicMock()

        db.query.return_value.filter.return_value.first.return_value = (
            embedding_mock
        )

        resultado = repository.buscar_por_foto_id(foto_id)

        db.query.assert_called_once_with(mock_model)

        db.query.return_value.filter.assert_called_once()

        assert resultado is embedding_mock

    @patch("app.embeddings.repository.EmbeddingFacial")
    def test_buscar_por_foto_id_nao_encontrado(
        self, mock_model, repository, db
    ):

        foto_id = uuid.uuid4()

        db.query.return_value.filter.return_value.first.return_value = None

        resultado = repository.buscar_por_foto_id(foto_id)

        assert resultado is None

    @patch("app.embeddings.repository.EmbeddingFacial")
    def test_buscar_mais_semelhante(
        self, mock_model, repository, db
    ):

        vetor = [0.2] * 512

        embedding_mock = MagicMock()
        distancia_mock = MagicMock()

        mock_model.vetor.cosine_distance.return_value = distancia_mock

        db.query.return_value.order_by.return_value.first.return_value = (
            (embedding_mock, 0.15)
        )

        resultado = repository.buscar_mais_semelhante(vetor)

        db.query.assert_called_once_with(
            mock_model,
            distancia_mock.label.return_value
        )

        assert mock_model.vetor.cosine_distance.call_count == 2

        db.query.return_value.order_by.assert_called_once_with(
            distancia_mock
        )

        assert resultado == (embedding_mock, 0.15)

    @patch("app.embeddings.repository.EmbeddingFacial")
    def test_buscar_mais_semelhante_sem_resultado(
        self, mock_model, repository, db
    ):

        vetor = [0.3] * 512

        mock_model.vetor.cosine_distance.return_value = MagicMock()

        db.query.return_value.order_by.return_value.first.return_value = None

        resultado = repository.buscar_mais_semelhante(vetor)

        assert resultado is None


# ==========================================================
# SERVICE
# ==========================================================

class TestEmbeddingService:

    @pytest.fixture
    def model(self):
        return MagicMock()

    @pytest.fixture
    def service(self, model):
        service = EmbeddingService.__new__(EmbeddingService)
        service.model = model

        return service

    def test_inicializar_service(self):

        with patch(
            "app.embeddings.service.FaceNet"
        ) as mock_facenet:

            service = EmbeddingService()

            mock_facenet.assert_called_once()

            assert service.model is mock_facenet.return_value

    def test_imagem_invalida(self, service):

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=None
        ):

            with pytest.raises(
                ValueError,
                match="Não foi possível carregar a imagem."
            ):

                service.gerar_embedding(b"imagem_invalida")

    def test_nenhum_rosto_detectado(self, service):

        imagem = np.zeros((100, 100, 3), dtype=np.uint8)

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=imagem
        ), patch(
            "app.embeddings.service.RetinaFace.detect_faces",
            return_value={}
        ):

            with pytest.raises(
                ValueError,
                match="Nenhum rosto foi detectado na imagem."
            ):

                service.gerar_embedding(b"imagem")

    def test_mais_de_um_rosto_detectado(self, service):

        imagem = np.zeros((100, 100, 3), dtype=np.uint8)

        faces = {
            "face_1": {"facial_area": [10, 10, 50, 50]},
            "face_2": {"facial_area": [50, 50, 90, 90]}
        }

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=imagem
        ), patch(
            "app.embeddings.service.RetinaFace.detect_faces",
            return_value=faces
        ):

            with pytest.raises(
                ValueError,
                match="Mais de um rosto foi detectado na imagem."
            ):

                service.gerar_embedding(b"imagem")

    def test_recorte_do_rosto_vazio(self, service):

        imagem = np.zeros((100, 100, 3), dtype=np.uint8)

        faces = {
            "face_1": {
                "facial_area": [150, 150, 200, 200]
            }
        }

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=imagem
        ), patch(
            "app.embeddings.service.RetinaFace.detect_faces",
            return_value=faces
        ):

            with pytest.raises(
                ValueError,
                match="Não foi possível recortar o rosto."
            ):

                service.gerar_embedding(b"imagem")

    def test_gerar_embedding_com_sucesso(self, service):

        imagem = np.zeros((100, 100, 3), dtype=np.uint8)

        # Simula uma imagem BGR com valores conhecidos.
        imagem[10:50, 10:50] = [10, 20, 30]

        faces = {
            "face_1": {
                "facial_area": [10, 10, 50, 50]
            }
        }

        vetor_esperado = np.array(
            [[0.1] * 512],
            dtype=np.float32
        )

        service.model.embeddings.return_value = vetor_esperado

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=imagem
        ), patch(
            "app.embeddings.service.RetinaFace.detect_faces",
            return_value=faces
        ):

            resultado = service.gerar_embedding(b"imagem")

        assert isinstance(resultado, list)
        assert len(resultado) == 512
        assert resultado == vetor_esperado[0].tolist()

        service.model.embeddings.assert_called_once()

        rosto_enviado = service.model.embeddings.call_args[0][0][0]

        assert rosto_enviado.shape == (40, 40, 3)

        # Confirma a conversão BGR para RGB.
        assert np.array_equal(
            rosto_enviado[0, 0],
            [30, 20, 10]
        )

    def test_gerar_embedding_utiliza_um_unico_rosto(
        self, service
    ):

        imagem = np.zeros((100, 100, 3), dtype=np.uint8)

        faces = {
            "face_1": {
                "facial_area": [10, 10, 50, 50]
            }
        }

        service.model.embeddings.return_value = np.zeros(
            (1, 512),
            dtype=np.float32
        )

        with patch(
            "app.embeddings.service.cv2.imdecode",
            return_value=imagem
        ), patch(
            "app.embeddings.service.RetinaFace.detect_faces",
            return_value=faces
        ):

            service.gerar_embedding(b"imagem")

        service.model.embeddings.assert_called_once()

        rosto_enviado = service.model.embeddings.call_args[0][0]

        assert len(rosto_enviado) == 1
