from uuid import UUID

from app.enderecos.model import Endereco
from app.enderecos.repository import EnderecoRepository
from app.enderecos.schema import EnderecoCreate, EnderecoUpdate
from app.pessoas.model import Pessoa


class EnderecoService:

    def __init__(self, repository: EnderecoRepository):
        self.repository = repository

    def criar(self, dados: EnderecoCreate):

        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == dados.pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        endereco = Endereco(
            pessoa_id=dados.pessoa_id,
            logradouro=dados.logradouro,
            numero=dados.numero,
            bairro=dados.bairro,
            cidade=dados.cidade,
            estado=dados.estado,
            cep=dados.cep
        )

        return self.repository.salvar(endereco)

    def listar(self):
        return self.repository.listar()

    def buscar_por_id(self, id: UUID):

        endereco = self.repository.buscar_por_id(id)

        if not endereco:
            raise ValueError("Endereço não encontrado.")

        return endereco

    def listar_por_pessoa(self, pessoa_id: UUID):

        pessoa = (
            self.repository.db.query(Pessoa)
            .filter(Pessoa.id == pessoa_id)
            .first()
        )

        if not pessoa:
            raise ValueError("Pessoa não encontrada.")

        return self.repository.buscar_por_pessoa(pessoa_id)

    def atualizar(self, id: UUID, dados: EnderecoUpdate):

        endereco = self.repository.buscar_por_id(id)

        if not endereco:
            raise ValueError("Endereço não encontrado.")

        if dados.logradouro is not None:
            endereco.logradouro = dados.logradouro

        if dados.numero is not None:
            endereco.numero = dados.numero

        if dados.bairro is not None:
            endereco.bairro = dados.bairro

        if dados.cidade is not None:
            endereco.cidade = dados.cidade

        if dados.estado is not None:
            endereco.estado = dados.estado

        if dados.cep is not None:
            endereco.cep = dados.cep

        return self.repository.atualizar(endereco)

    def deletar(self, id: UUID):

        endereco = self.repository.buscar_por_id(id)

        if not endereco:
            raise ValueError("Endereço não encontrado.")

        self.repository.deletar(endereco)