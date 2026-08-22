from app.database import engine

try:
    with engine.connect() as conexao:
        print("Conexão realizada com sucesso!")
except Exception as e:
    print("Erro ao conectar:")
    print(e)