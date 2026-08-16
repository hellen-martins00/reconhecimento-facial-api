from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

# é usada quando o cliente envia dados para criar uma pessoa
# apenas valida os dados
class PessoaCreate(BaseModel):

    # obrigatório, mínimo 3 letras, máximo 150
    nome: str = Field(..., min_length=3, max_length=150)

    # deve possuir exatamente 11 caracteres
    cpf: str = Field(..., min_length=11, max_length=11)

    data_nascimento: date

    sexo: str = Field(..., min_length=1, max_length=1)

    nome_mae: str

    nome_pai: str
    
class PessoaUpdate(BaseModel):
    
    nome: Optional[str] = Field(None, min_length=3, max_length=150)

    cpf: Optional[str] = Field(None, min_length=11, max_length=11)

    data_nascimento: Optional[date] = None

    sexo: Optional[str] = Field(None, min_length=1, max_length=1)

    nome_mae: Optional[str] = None

    nome_pai: Optional[str] = None
    
# é usada quando a API devolve uma pessoa para o cliente
class PessoaResponse(BaseModel):

    id: UUID

    nome: str

    cpf: str

    data_nascimento: date

    sexo: str

    nome_mae: str

    nome_pai: str

    model_config = {
        "from_attributes": True
    }