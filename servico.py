"""Camada de serviço: junta banco, BST, dicionário, POO e IA."""

from estruturas import ArvoreBST
from ia import triar_ticket
from modelos import Atendente, Cliente, Ticket


class CentralSAC:
    def __init__(self, banco):
        self.banco = banco
        self.indice_tickets = ArvoreBST()   # BST: ID -> Ticket
        self.indice_categorias = {}         # dicionário: categoria -> [IDs]
        self._carregar_indices()

    # ----------------------------------------------------------- índices
    def _carregar_indices(self):
        """Ao iniciar, lê os tickets do banco e monta BST e dicionário."""
        tickets = self.banco.listar_tickets()  # já vem ordenado por ID
        self.indice_tickets.construir_balanceada([(t.id, t) for t in tickets])
        self.indice_categorias = {}
        for ticket in tickets:
            self._indexar_categoria(ticket)

    def _indexar_categoria(self, ticket):
        self.indice_categorias.setdefault(ticket.categoria, []).append(ticket.id)

    def _desindexar_categoria(self, ticket):
        ids = self.indice_categorias.get(ticket.categoria, [])
        if ticket.id in ids:
            ids.remove(ticket.id)
        if not ids:
            self.indice_categorias.pop(ticket.categoria, None)

    # ---------------------------------------------------- clientes/atendentes
    def cadastrar_cliente(self, nome, email, endereco, plano):
        if not nome.strip() or not email.strip():
            raise ValueError("Nome e e-mail são obrigatórios.")
        cliente = Cliente(nome.strip(), email.strip(), endereco.strip(), plano.strip() or "Básico")
        self.banco.inserir_cliente(cliente)
        return cliente

    def buscar_cliente(self, cliente_id):
        return self.banco.buscar_cliente(cliente_id)

    def listar_clientes(self):
        return self.banco.listar_clientes()

    def cadastrar_atendente(self, nome, email, setor):
        if not nome.strip() or not email.strip():
            raise ValueError("Nome e e-mail são obrigatórios.")
        atendente = Atendente(nome.strip(), email.strip(), setor.strip() or "Suporte Técnico")
        self.banco.inserir_atendente(atendente)
        return atendente

    def listar_atendentes(self):
        return self.banco.listar_atendentes()

    # ------------------------------------------------------------ tickets
    def abrir_ticket(self, cliente_id, descricao):
        if not descricao.strip():
            raise ValueError("A descrição não pode ficar vazia.")
        if self.banco.buscar_cliente(cliente_id) is None:
            raise ValueError("Cliente não encontrado.")

        categoria, resposta, origem = triar_ticket(descricao)   # IA
        ticket = Ticket(cliente_id, descricao.strip(), categoria, resposta)
        self.banco.inserir_ticket(ticket)                       # banco (gera o ID)
        self.indice_tickets.inserir(ticket.id, ticket)          # BST
        self._indexar_categoria(ticket)                         # dicionário
        return ticket, origem

    def buscar_ticket(self, ticket_id):
        return self.indice_tickets.buscar(ticket_id)

    def listar_tickets(self):
        return self.indice_tickets.em_ordem()

    def tickets_por_categoria(self, categoria):
        ids = self.indice_categorias.get(categoria, [])
        return [self.indice_tickets.buscar(i) for i in ids]

    def resumo_categorias(self):
        return {cat: len(ids) for cat, ids in self.indice_categorias.items()}

    def assumir_ticket(self, ticket_id, atendente_id):
        ticket = self._ticket_ou_erro(ticket_id)
        self._atendente_ou_erro(atendente_id)
        ticket.assumir(atendente_id)
        self.banco.atualizar_ticket(ticket)
        return ticket

    def resolver_ticket(self, ticket_id, atendente_id, resolucao):
        ticket = self._ticket_ou_erro(ticket_id)
        self._atendente_ou_erro(atendente_id)
        ticket.resolver(atendente_id, resolucao)
        self.banco.atualizar_ticket(ticket)
        return ticket

    def excluir_ticket(self, ticket_id):
        ticket = self._ticket_ou_erro(ticket_id)
        self.banco.excluir_ticket(ticket_id)
        self.indice_tickets.remover(ticket_id)
        self._desindexar_categoria(ticket)

    # ---------------------------------------------------------- auxiliares
    def _ticket_ou_erro(self, ticket_id):
        ticket = self.indice_tickets.buscar(ticket_id)
        if ticket is None:
            raise ValueError("Ticket não encontrado.")
        return ticket

    def _atendente_ou_erro(self, atendente_id):
        if self.banco.buscar_atendente(atendente_id) is None:
            raise ValueError("Atendente não encontrado.")
