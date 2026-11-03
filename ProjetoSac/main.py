"""Interface de terminal do SAC. Execute com: python main.py"""

import os
import sqlite3

from banco import BancoDeDados
from servico import CentralSAC


def ler_inteiro(mensagem):
    while True:
        valor = input(mensagem).strip()
        if valor.isdigit():
            return int(valor)
        print("Digite apenas números.")


def cadastrar_cliente(sac):
    nome = input("Nome: ")
    email = input("E-mail: ")
    endereco = input("Endereço: ")
    plano = input("Plano (ex.: 300 Mega) [Básico]: ")
    cliente = sac.cadastrar_cliente(nome, email, endereco, plano)
    print(f"Cliente cadastrado: {cliente.resumo()}")


def cadastrar_atendente(sac):
    nome = input("Nome: ")
    email = input("E-mail: ")
    setor = input("Setor [Suporte Técnico]: ")
    atendente = sac.cadastrar_atendente(nome, email, setor)
    print(f"Atendente cadastrado: {atendente.resumo()}")


def abrir_ticket(sac):
    for c in sac.listar_clientes():
        print("  ", c.resumo())
    cliente_id = ler_inteiro("ID do cliente: ")
    descricao = input("Descreva o problema: ")
    print("Analisando o relato...")
    ticket, origem = sac.abrir_ticket(cliente_id, descricao)
    print(f"\nTicket #{ticket.id} aberto. Triagem feita por: {origem}")
    print(f"Categoria: {ticket.categoria}")
    print(f"Resposta automática: {ticket.resposta_ia}")


def buscar_ticket(sac):
    ticket = sac.buscar_ticket(ler_inteiro("ID do ticket: "))
    if ticket is None:
        print("Ticket não encontrado.")
        return
    cliente = sac.buscar_cliente(ticket.cliente_id)
    print(ticket.detalhes())
    print(f"Cliente:    {cliente.resumo() if cliente else '-'}")


def listar_tickets(sac):
    tickets = sac.listar_tickets()
    if not tickets:
        print("Nenhum ticket cadastrado.")
    for t in tickets:
        print(t.resumo())


def listar_por_categoria(sac):
    resumo = sac.resumo_categorias()
    if not resumo:
        print("Nenhum ticket cadastrado.")
        return
    print("Categorias:", ", ".join(f"{c} ({n})" for c, n in resumo.items()))
    categoria = input("Categoria: ").strip()
    tickets = sac.tickets_por_categoria(categoria)
    if not tickets:
        print("Nenhum ticket nessa categoria.")
    for t in tickets:
        print(t.resumo())


def assumir_ticket(sac):
    for a in sac.listar_atendentes():
        print("  ", a.resumo())
    ticket_id = ler_inteiro("ID do ticket: ")
    atendente_id = ler_inteiro("ID do atendente: ")
    ticket = sac.assumir_ticket(ticket_id, atendente_id)
    print(f"Ticket #{ticket.id} agora está: {ticket.status}")


def resolver_ticket(sac):
    for a in sac.listar_atendentes():
        print("  ", a.resumo())
    ticket_id = ler_inteiro("ID do ticket: ")
    atendente_id = ler_inteiro("ID do atendente: ")
    resolucao = input("Resolução aplicada: ")
    ticket = sac.resolver_ticket(ticket_id, atendente_id, resolucao)
    print(f"Ticket #{ticket.id} agora está: {ticket.status}")


def excluir_ticket(sac):
    sac.excluir_ticket(ler_inteiro("ID do ticket a excluir: "))
    print("Ticket excluído.")


def mostrar_arvore(sac):
    arvore = sac.indice_tickets
    print(f"Tickets na BST: {arvore.tamanho} | Altura da árvore: {arvore.altura()}")


# Tabela de opções: cada tecla aponta para (texto do menu, função).
OPCOES = {
    "1": ("Cadastrar cliente", cadastrar_cliente),
    "2": ("Cadastrar atendente", cadastrar_atendente),
    "3": ("Abrir ticket (triagem com IA)", abrir_ticket),
    "4": ("Buscar ticket por ID (BST)", buscar_ticket),
    "5": ("Listar todos os tickets (em ordem de ID)", listar_tickets),
    "6": ("Listar tickets por categoria (dicionário)", listar_por_categoria),
    "7": ("Assumir ticket", assumir_ticket),
    "8": ("Resolver ticket", resolver_ticket),
    "9": ("Excluir ticket", excluir_ticket),
    "10": ("Ver tamanho e altura da BST", mostrar_arvore),
}


def main():
    banco = BancoDeDados(os.environ.get("SAC_DB", "sac.db"))
    sac = CentralSAC(banco)

    try:
        while True:
            print("\n=== SAC - Central de Atendimento ===")
            for tecla, (texto, _) in OPCOES.items():
                print(f"{tecla:>2} - {texto}")
            print(" 0 - Sair")

            escolha = input("Opção: ").strip()
            if escolha == "0":
                break
            if escolha not in OPCOES:
                print("Opção inválida.")
                continue
            try:
                OPCOES[escolha][1](sac)
            except (ValueError, sqlite3.IntegrityError) as erro:
                print(f"Erro: {erro}")
    except (EOFError, KeyboardInterrupt):
        print()
    finally:
        banco.fechar()
        print("Até logo!")


if __name__ == "__main__":
    main()
