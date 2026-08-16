import cv2
import numpy as np

from retinaface import RetinaFace
from keras_facenet import FaceNet


CAMINHO_IMAGEM = "tests/imagens/foto_hellen2.jpg"


print("Carregando FaceNet...")

embedder = FaceNet()

print("FaceNet carregado com sucesso!")


print("Detectando rosto com RetinaFace...")

faces = RetinaFace.detect_faces(CAMINHO_IMAGEM)


if not faces:
    print("Nenhum rosto foi encontrado.")
    exit()


print(f"Rostos encontrados: {len(faces)}")


# Pega o primeiro rosto encontrado
primeiro_rosto = list(faces.values())[0]

print("Rosto detectado com sucesso!")


print("Carregando imagem...")

imagem = cv2.imread(CAMINHO_IMAGEM)

if imagem is None:
    print("Não foi possível carregar a imagem.")
    exit()

imagem = cv2.cvtColor(imagem, cv2.COLOR_BGR2RGB)

print("Imagem carregada com sucesso!")

print("Gerando embedding facial...")

embedding = embedder.embeddings([imagem])

print("Embedding gerado com sucesso!")

print(f"Formato do embedding: {embedding.shape}")

print(f"Quantidade de dimensões: {embedding.shape[1]}")