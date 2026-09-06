from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# CRIAÇÃO DE PESSOA

class PessoaCreate(BaseModel):

    nome: str = Field(
        ...,
        min_length=3,
        max_length=150,
        description="Nome completo da pessoa."
    )

    cpf: str = Field(
        ...,
        min_length=11,
        max_length=11,
        description="CPF contendo exatamente 11 números."
    )

    data_nascimento: date

    sexo: str = Field(
        ...,
        min_length=1,
        max_length=1,
        description="Sexo: M ou F."
    )

    nome_mae: str = Field(
        ...,
        min_length=3,
        max_length=150
    )

    nome_pai: str = Field(
        ...,
        min_length=3,
        max_length=150
    )

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, valor):
        if not valor.isdigit():
            raise ValueError(
                "O CPF deve conter apenas números."
            )

        if len(valor) != 11:
            raise ValueError(
                "O CPF deve conter exatamente 11 números."
            )

        return valor

    @field_validator("sexo")
    @classmethod
    def validar_sexo(cls, valor):
        valor = valor.upper()

        if valor not in ("M", "F"):
            raise ValueError(
                "O sexo deve ser M ou F."
            )

        return valor

    @field_validator("nome", "nome_mae", "nome_pai")
    @classmethod
    def validar_nomes(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O nome não pode ficar vazio."
            )

        return valor

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, valor):
        if valor > date.today():
            raise ValueError(
                "A data de nascimento não pode ser futura."
            )

        return valor


# ATUALIZAÇÃO DE PESSOA

class PessoaUpdate(BaseModel):

    nome: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150
    )

    cpf: Optional[str] = Field(
        None,
        min_length=11,
        max_length=11
    )

    data_nascimento: Optional[date] = None

    sexo: Optional[str] = Field(
        None,
        min_length=1,
        max_length=1
    )

    nome_mae: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150
    )

    nome_pai: Optional[str] = Field(
        None,
        min_length=3,
        max_length=150
    )

    @field_validator("cpf")
    @classmethod
    def validar_cpf(cls, valor):
        if not valor.isdigit():
            raise ValueError(
                "O CPF deve conter apenas números."
            )

        if len(valor) != 11:
            raise ValueError(
                "O CPF deve conter exatamente 11 números."
            )

        return valor

    @field_validator("sexo")
    @classmethod
    def validar_sexo(cls, valor):
        valor = valor.upper()

        if valor not in ("M", "F"):
            raise ValueError(
                "O sexo deve ser M ou F."
            )

        return valor

    @field_validator("nome", "nome_mae", "nome_pai")
    @classmethod
    def validar_nomes(cls, valor):
        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O nome não pode ficar vazio."
            )

        return valor

    @field_validator("data_nascimento")
    @classmethod
    def validar_data_nascimento(cls, valor):
        if valor > date.today():
            raise ValueError(
                "A data de nascimento não pode ser futura."
            )

        return valor


# RESPOSTA DE UMA PESSOA

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


# RESPOSTA DA LISTAGEM DE PESSOAS

class PessoaListaResponse(BaseModel):

    id: UUID

    nome: str

    cpf: str

    data_nascimento: date

    sexo: str

    nome_mae: str

    nome_pai: str

    foto_id: Optional[UUID] = None