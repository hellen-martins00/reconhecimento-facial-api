from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do banco
DATABASE_URL = os.getenv("DATABASE_URL")

# Usa o driver psycopg 3 (psycopg2-binary causava segfault ao conectar)
if DATABASE_URL:
    for prefixo in ("postgres://", "postgresql://"):
        if DATABASE_URL.startswith(prefixo):
            DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL[len(prefixo):]
            break

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY")