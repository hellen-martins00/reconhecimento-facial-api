from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.pessoas.model import Pessoa
from app.fotos.model import Foto


class PessoaRepository:

    def __init__(self, db: Session):
        self.db = db

    # SALVAR PESSOA

    def salvar(self, pessoa: Pessoa):

        try:

            self.db.add(pessoa)

            self.db.commit()

            self.db.refresh(pessoa)

            return pessoa

        except Exception:

            self.db.rollback()

            raise

    # BUSCAR POR CPF

    def buscar_por_cpf(self, cpf: str):

        return (
            self.db.query(Pessoa)
            .filter(Pessoa.cpf == cpf)
            .first()
        )

    # BUSCAR POR ID

    def buscar_por_id(self, id: UUID):

        return (
            self.db.query(Pessoa)
            .filter(Pessoa.id == id)
            .first()
        )

    # LISTAR PESSOAS

    def listar(self):

        fotos_ranqueadas = (
            self.db.query(
                Foto.id.label("foto_id"),
                Foto.pessoa_id,
                func.row_number()
                .over(
                    partition_by=Foto.pessoa_id,
                    order_by=[
                        Foto.data_upload.desc(),
                        Foto.id.desc()
                    ]
                )
                .label("numero")
            )
            .filter(Foto.pessoa_id.isnot(None))
            .subquery()
        )

        return (
            self.db.query(
                Pessoa,
                fotos_ranqueadas.c.foto_id
            )
            .outerjoin(
                fotos_ranqueadas,
                (
                    fotos_ranqueadas.c.pessoa_id == Pessoa.id
                )
                & (
                    fotos_ranqueadas.c.numero == 1
                )
            )
            .all()
        )

    # ATUALIZAR PESSOA

    def atualizar(self, pessoa: Pessoa):

        try:

            self.db.commit()

            self.db.refresh(pessoa)

            return pessoa

        except Exception:

            self.db.rollback()

            raise

    # DELETAR PESSOA

    def deletar(self, pessoa: Pessoa):

        try:

            self.db.delete(pessoa)

            self.db.commit()

        except Exception:

            self.db.rollback()

            raise