from dotenv import load_dotenv
import os

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do banco
DATABASE_URL = os.getenv("DATABASE_URL")

# Configurações de autenticação
SECRET_KEY = os.getenv("SECRET_KEY")