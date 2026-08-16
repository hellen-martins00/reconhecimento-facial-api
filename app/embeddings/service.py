import cv2
import numpy as np

from retinaface import RetinaFace
from keras_facenet import FaceNet


class EmbeddingService:

    def __init__(self):

        print("Carregando FaceNet...")

        self.model = FaceNet()

        print("FaceNet carregado com sucesso!")

    def gerar_embedding(
        self,
        conteudo: bytes
    ) -> list[float]:

        # 1. Converter os bytes da imagem para um array
        imagem_bytes = np.frombuffer(
            conteudo,
            dtype=np.uint8
        )

        # 2. Carregar a imagem diretamente da memória
        imagem = cv2.imdecode(
            imagem_bytes,
            cv2.IMREAD_COLOR
        )

        if imagem is None:
            raise ValueError(
                "Não foi possível carregar a imagem."
            )

        # 3. Detectar rosto
        print("Detectando rosto com RetinaFace...")

        faces = RetinaFace.detect_faces(imagem)

        if not faces:
            raise ValueError(
                "Nenhum rosto foi detectado na imagem."
            )

        quantidade_rostos = len(faces)

        print(
            f"Rostos encontrados: {quantidade_rostos}"
        )

        # O reconhecimento trabalha somente
        # com uma pessoa por imagem
        if quantidade_rostos > 1:

            raise ValueError(
                "Mais de um rosto foi detectado na imagem. "
                "Envie uma imagem contendo apenas uma pessoa."
            )

        # 4. Obter o único rosto encontrado
        face = list(faces.values())[0]

        area = face["facial_area"]

        x1, y1, x2, y2 = area

        # 5. Recortar o rosto
        rosto = imagem[
            y1:y2,
            x1:x2
        ]

        if rosto.size == 0:

            raise ValueError(
                "Não foi possível recortar o rosto."
            )

        # 6. Converter BGR → RGB
        rosto = cv2.cvtColor(
            rosto,
            cv2.COLOR_BGR2RGB
        )

        # 7. Gerar embedding
        print("Gerando embedding facial...")

        embedding = self.model.embeddings(
            [rosto]
        )

        # embedding possui formato (1, 512)
        vetor = embedding[0]

        print(
            "Embedding gerado com sucesso!"
        )

        print(
            f"Dimensões: {len(vetor)}"
        )

        return vetor.tolist()