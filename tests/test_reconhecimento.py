
import importlib
from io import BytesIO
from types import SimpleNamespace
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.reconhecimento.model import Reconhecimento
from app.reconhecimento.repository import ReconhecimentoRepository


router = importlib.import_module("app.reconhecimento.router")


# ==========================================================
# FIXTURES
# ==========================================================

@pytest.fixture
def db():
    return MagicMock()


@pytest.fixture
def agente():
    return SimpleNamespace(id=uuid4())


@pytest.fixture
def pessoa():
    return SimpleNamespace(
        id=uuid4(),
        nome="Maria Silva",
        cpf="12345678901"
    )


@pytest.fixture
def foto():
    return SimpleNamespace(
        id=uuid4(),
        nome_arquivo="foto.jpg",
        data_upload=__import__("datetime").datetime(2026, 1, 10)
    )


@pytest.fixture
def resultado_reconhecido(pessoa, foto):
    return {
        "reconhecido": True,
        "distancia": 0.25,
        "pessoa": pessoa,
        "foto": foto
    }


@pytest.fixture
def arquivo_valido():
    return SimpleNamespace(
        filename="imagem.jpg",
        file=BytesIO(b"conteudo-da-imagem")
    )


# ==========================================================
# REPOSITORY
# ==========================================================

class TestReconhecimentoRepository:

    def test_criar(self, db):
        reconhecimento = Reconhecimento(
            agente_id=uuid4(),
            reconhecido=True,
            distancia=0.25
        )

        repository = ReconhecimentoRepository(db)

        resultado = repository.criar(reconhecimento)

        db.add.assert_called_once_with(reconhecimento)
        db.commit.assert_called_once()
        db.refresh.assert_called_once_with(reconhecimento)

        assert resultado is reconhecimento

    def test_contar_total(self, db):
        db.query.return_value.count.return_value = 15

        repository = ReconhecimentoRepository(db)

        resultado = repository.contar_total()

        db.query.assert_called_once_with(Reconhecimento)
        assert resultado == 15

    def test_listar_ultimos_com_limite_padrao(self, db):
        reconhecimentos = [MagicMock(), MagicMock()]

        query = db.query.return_value
        query.order_by.return_value.limit.return_value.all.return_value = (
            reconhecimentos
        )

        repository = ReconhecimentoRepository(db)

        resultado = repository.listar_ultimos()

        assert resultado == reconhecimentos
        query.order_by.assert_called_once()
        query.order_by.return_value.limit.assert_called_once_with(5)

    def test_listar_ultimos_com_limite_personalizado(self, db):
        reconhecimentos = [MagicMock()]

        query = db.query.return_value
        query.order_by.return_value.limit.return_value.all.return_value = (
            reconhecimentos
        )

        repository = ReconhecimentoRepository(db)

        resultado = repository.listar_ultimos(limite=10)

        assert resultado == reconhecimentos
        query.order_by.return_value.limit.assert_called_once_with(10)


# ==========================================================
# ROUTER - POST /reconhecimento
# ==========================================================

class TestReconhecerRosto:

    def test_rejeita_extensao_nao_permitida(
        self, db, agente
    ):
        arquivo = SimpleNamespace(
            filename="imagem.pdf",
            file=BytesIO(b"conteudo")
        )

        with pytest.raises(HTTPException) as exc:
            router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        assert exc.value.status_code == 400
        assert "Formato de imagem não permitido" in exc.value.detail

    @pytest.mark.parametrize(
        "extensao",
        [".jpg", ".jpeg", ".png"]
    )
    def test_aceita_extensoes_permitidas(
        self,
        extensao,
        db,
        agente,
        resultado_reconhecido
    ):
        arquivo = SimpleNamespace(
            filename=f"imagem{extensao}",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(
                router,
                "EmbeddingRepository"
            ) as embedding_repo,
            patch.object(
                router,
                "ReconhecimentoService"
            ) as service_class,
            patch.object(
                router,
                "ReconhecimentoRepository"
            ) as reconhecimento_repo
        ):
            service_class.return_value.reconhecer.return_value = (
                resultado_reconhecido
            )

            resultado = router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        embedding_repo.assert_called_once_with(db)
        service_class.assert_called_once_with(
            embedding_repo.return_value
        )
        service_class.return_value.reconhecer.assert_called_once_with(
            b"conteudo"
        )
        reconhecimento_repo.assert_called_once_with(db)
        reconhecimento_repo.return_value.criar.assert_called_once()

        assert resultado["reconhecido"] is True
        assert resultado["pessoa"]["nome"] == "Maria Silva"
        assert resultado["foto"]["nome_arquivo"] == "foto.jpg"

    def test_rejeita_arquivo_vazio(self, db, agente):
        arquivo = SimpleNamespace(
            filename="imagem.jpg",
            file=BytesIO(b"")
        )

        with pytest.raises(HTTPException) as exc:
            router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        assert exc.value.status_code == 400
        assert exc.value.detail == "O arquivo enviado está vazio."

    def test_reconhecimento_sem_correspondencia(
        self, db, agente
    ):
        resultado_service = {
            "reconhecido": False,
            "distancia": None,
            "pessoa": None,
            "foto": None
        }

        arquivo = SimpleNamespace(
            filename="imagem.png",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(router, "EmbeddingRepository"),
            patch.object(router, "ReconhecimentoService") as service_class,
            patch.object(
                router,
                "ReconhecimentoRepository"
            ) as reconhecimento_repo
        ):
            service_class.return_value.reconhecer.return_value = (
                resultado_service
            )

            resultado = router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        assert resultado == resultado_service

        reconhecimento_salvo = (
            reconhecimento_repo.return_value.criar.call_args[0][0]
        )

        assert reconhecimento_salvo.pessoa_id is None
        assert reconhecimento_salvo.agente_id == agente.id
        assert reconhecimento_salvo.reconhecido is False
        assert reconhecimento_salvo.distancia is None

    def test_converte_value_error_em_http_400(
        self, db, agente
    ):
        arquivo = SimpleNamespace(
            filename="imagem.jpg",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(router, "EmbeddingRepository"),
            patch.object(router, "ReconhecimentoService") as service_class
        ):
            service_class.return_value.reconhecer.side_effect = (
                ValueError("Nenhum rosto encontrado.")
            )

            with pytest.raises(HTTPException) as exc:
                router.reconhecer_rosto(
                    arquivo=arquivo,
                    db=db,
                    agente_atual=agente
                )

        assert exc.value.status_code == 400
        assert exc.value.detail == "Nenhum rosto encontrado."

    def test_repassa_excecao_inesperada(
        self, db, agente
    ):
        arquivo = SimpleNamespace(
            filename="imagem.jpg",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(router, "EmbeddingRepository"),
            patch.object(router, "ReconhecimentoService") as service_class,
            patch.object(router.logger, "exception") as logger
        ):
            service_class.return_value.reconhecer.side_effect = (
                RuntimeError("Erro interno")
            )

            with pytest.raises(RuntimeError, match="Erro interno"):
                router.reconhecer_rosto(
                    arquivo=arquivo,
                    db=db,
                    agente_atual=agente
                )

        logger.assert_called_once_with(
            "Erro interno na rota de reconhecimento"
        )

    def test_reconhecimento_sem_pessoa_mas_com_foto(
        self, db, agente, foto
    ):
        resultado_service = {
            "reconhecido": False,
            "distancia": 0.75,
            "pessoa": None,
            "foto": foto
        }

        arquivo = SimpleNamespace(
            filename="imagem.jpg",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(router, "EmbeddingRepository"),
            patch.object(router, "ReconhecimentoService") as service_class,
            patch.object(router, "ReconhecimentoRepository")
        ):
            service_class.return_value.reconhecer.return_value = (
                resultado_service
            )

            resultado = router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        assert resultado["pessoa"] is None
        assert resultado["foto"]["id"] == foto.id
        assert resultado["foto"]["nome_arquivo"] == foto.nome_arquivo

    def test_reconhecimento_com_pessoa_sem_foto(
        self, db, agente, pessoa
    ):
        resultado_service = {
            "reconhecido": True,
            "distancia": 0.30,
            "pessoa": pessoa,
            "foto": None
        }

        arquivo = SimpleNamespace(
            filename="imagem.jpg",
            file=BytesIO(b"conteudo")
        )

        with (
            patch.object(router, "EmbeddingRepository"),
            patch.object(router, "ReconhecimentoService") as service_class,
            patch.object(router, "ReconhecimentoRepository")
        ):
            service_class.return_value.reconhecer.return_value = (
                resultado_service
            )

            resultado = router.reconhecer_rosto(
                arquivo=arquivo,
                db=db,
                agente_atual=agente
            )

        assert resultado["pessoa"]["id"] == pessoa.id
        assert resultado["foto"] is None


# ==========================================================
# ROUTER - GET /reconhecimento/total
# ==========================================================

class TestTotalReconhecimentos:

    def test_retorna_total(self, db, agente):
        with patch.object(
            router,
            "ReconhecimentoRepository"
        ) as repository_class:
            repository_class.return_value.contar_total.return_value = 25

            resultado = router.total_reconhecimentos(
                db=db,
                agente_atual=agente
            )

        repository_class.assert_called_once_with(db)
        repository_class.return_value.contar_total.assert_called_once()

        assert resultado == {"total": 25}

    def test_retorna_zero_quando_nao_existirem_registros(
        self, db, agente
    ):
        with patch.object(
            router,
            "ReconhecimentoRepository"
        ) as repository_class:
            repository_class.return_value.contar_total.return_value = 0

            resultado = router.total_reconhecimentos(
                db=db,
                agente_atual=agente
            )

        assert resultado == {"total": 0}
