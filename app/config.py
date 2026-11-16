from dotenv import load_dotenv
import os

# Identifica se a execução é de testes
AMBIENTE_TESTE = os.getenv("APP_ENV") == "test"

# Carrega o arquivo de ambiente correspondente
if AMBIENTE_TESTE:
    load_dotenv(".env.test", override=True)
else:
    load_dotenv(".env", override=True)

# Configurações do banco
DATABASE_URL = os.getenv("DATABASE_URL")

# Utiliza Psycopg 3
if DATABASE_URL:
    for prefixo in ("postgres://", "postgresql://"):
        if DATABASE_URL.startswith(prefixo):
            DATABASE_URL = (
                "postgresql+psycopg://"
                + DATABASE_URL[len(prefixo):]
            )
            break

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY")