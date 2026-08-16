from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

# Cria a conexão com o banco
engine = create_engine(DATABASE_URL)

# Cria uma fábrica de sessões
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit=False,
    bind=engine
)

# Classe base para todos os modelos
class Base(DeclarativeBase):
    pass