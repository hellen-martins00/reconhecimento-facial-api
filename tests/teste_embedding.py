from app.embeddings.service import EmbeddingService


CAMINHO_IMAGEM = "tests/imagens/foto_hellen2.jpg"


print("Iniciando teste de embedding...")

service = EmbeddingService()

vetor = service.gerar_embedding(CAMINHO_IMAGEM)

print()
print("================================")
print("TESTE CONCLUÍDO COM SUCESSO")
print("================================")
print(f"Quantidade de dimensões: {len(vetor)}")
print(f"Primeiros valores: {vetor[:5]}")