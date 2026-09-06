from uuid import UUID

from pydantic import BaseModel, field_validator


class EnderecoCreate(BaseModel):

    pessoa_id: UUID

    logradouro: str

    numero: str

    bairro: str

    cidade: str

    estado: str

    cep: str

    @field_validator(
        "logradouro",
        "numero",
        "bairro",
        "cidade"
    )
    @classmethod
    def validar_textos(cls, valor, info):

        valor = valor.strip()

        if not valor:
            raise ValueError(
                f"O campo {info.field_name} é obrigatório."
            )

        limites = {
            "logradouro": (3, 200),
            "numero": (1, 20),
            "bairro": (2, 100),
            "cidade": (2, 100)
        }

        minimo, maximo = limites[info.field_name]

        if len(valor) < minimo:
            raise ValueError(
                f"O campo {info.field_name} deve ter "
                f"pelo menos {minimo} caracteres."
            )

        if len(valor) > maximo:
            raise ValueError(
                f"O campo {info.field_name} deve ter "
                f"no máximo {maximo} caracteres."
            )

        return valor

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):

        valor = valor.strip().upper()

        if len(valor) != 2:
            raise ValueError(
                "O estado deve conter exatamente 2 letras."
            )

        if not valor.isalpha():
            raise ValueError(
                "O estado deve conter apenas letras."
            )

        return valor

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, valor):

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O CEP é obrigatório."
            )

        if not valor.isdigit():
            raise ValueError(
                "O CEP deve conter apenas números."
            )

        if len(valor) != 8:
            raise ValueError(
                "O CEP deve conter exatamente 8 números."
            )

        return valor


class EnderecoUpdate(BaseModel):

    logradouro: str | None = None

    numero: str | None = None

    bairro: str | None = None

    cidade: str | None = None

    estado: str | None = None

    cep: str | None = None

    @field_validator(
        "logradouro",
        "numero",
        "bairro",
        "cidade"
    )
    @classmethod
    def validar_textos(cls, valor, info):

        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError(
                f"O campo {info.field_name} não pode ficar vazio."
            )

        limites = {
            "logradouro": (3, 200),
            "numero": (1, 20),
            "bairro": (2, 100),
            "cidade": (2, 100)
        }

        minimo, maximo = limites[info.field_name]

        if len(valor) < minimo:
            raise ValueError(
                f"O campo {info.field_name} deve ter "
                f"pelo menos {minimo} caracteres."
            )

        if len(valor) > maximo:
            raise ValueError(
                f"O campo {info.field_name} deve ter "
                f"no máximo {maximo} caracteres."
            )

        return valor

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip().upper()

        if len(valor) != 2:
            raise ValueError(
                "O estado deve conter exatamente 2 letras."
            )

        if not valor.isalpha():
            raise ValueError(
                "O estado deve conter apenas letras."
            )

        return valor

    @field_validator("cep")
    @classmethod
    def validar_cep(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip()

        if not valor:
            raise ValueError(
                "O CEP não pode ficar vazio."
            )

        if not valor.isdigit():
            raise ValueError(
                "O CEP deve conter apenas números."
            )

        if len(valor) != 8:
            raise ValueError(
                "O CEP deve conter exatamente 8 números."
            )

        return valor


class EnderecoResponse(BaseModel):

    id: UUID

    pessoa_id: UUID

    logradouro: str

    numero: str

    bairro: str

    cidade: str

    estado: str

    cep: str

    model_config = {
        "from_attributes": True
    }