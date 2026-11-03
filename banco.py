"""Persistência: banco SQLite (arquivo .db) e operações CRUD."""

import sqlite3

from modelos import Atendente, Cliente, Ticket


class BancoDeDados:
    def __init__(self, caminho="sac.db"):
        self.conexao = sqlite3.connect(caminho)
        self.conexao.row_factory = sqlite3.Row            # acessa colunas pelo nome
        self.conexao.execute("PRAGMA foreign_keys = ON")  # ativa as chaves estrangeiras
        self._criar_tabelas()

    def _criar_tabelas(self):
        with self.conexao:
            self.conexao.executescript("""
                CREATE TABLE IF NOT EXISTS clientes (
                    id       INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome     TEXT NOT NULL,
                    email    TEXT NOT NULL UNIQUE,
                    endereco TEXT,
                    plano    TEXT
                );
                CREATE TABLE IF NOT EXISTS atendentes (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome  TEXT NOT NULL,
                    email TEXT NOT NULL UNIQUE,
                    setor TEXT
                );
                CREATE TABLE IF NOT EXISTS tickets (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    cliente_id   INTEGER NOT NULL REFERENCES clientes(id),
                    atendente_id INTEGER REFERENCES atendentes(id),
                    descricao    TEXT NOT NULL,
                    categoria    TEXT,
                    resposta_ia  TEXT,
                    status       TEXT NOT NULL DEFAULT 'Aberto',
                    resolucao    TEXT,
                    criado_em    TEXT NOT NULL
                );
            """)

    # ------------------------------------------------------- clientes
    def inserir_cliente(self, cliente):
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO clientes (nome, email, endereco, plano) VALUES (?, ?, ?, ?)",
                (cliente.nome, cliente.email, cliente.endereco, cliente.plano),
            )
        cliente.id = cursor.lastrowid
        return cliente.id

    def buscar_cliente(self, cliente_id):
        linha = self.conexao.execute(
            "SELECT * FROM clientes WHERE id = ?", (cliente_id,)
        ).fetchone()
        return self._linha_para_cliente(linha) if linha else None

    def listar_clientes(self):
        linhas = self.conexao.execute("SELECT * FROM clientes ORDER BY id").fetchall()
        return [self._linha_para_cliente(l) for l in linhas]

    @staticmethod
    def _linha_para_cliente(linha):
        return Cliente(linha["nome"], linha["email"], linha["endereco"],
                       linha["plano"], linha["id"])

    # ----------------------------------------------------- atendentes
    def inserir_atendente(self, atendente):
        with self.conexao:
            cursor = self.conexao.execute(
                "INSERT INTO atendentes (nome, email, setor) VALUES (?, ?, ?)",
                (atendente.nome, atendente.email, atendente.setor),
            )
        atendente.id = cursor.lastrowid
        return atendente.id

    def buscar_atendente(self, atendente_id):
        linha = self.conexao.execute(
            "SELECT * FROM atendentes WHERE id = ?", (atendente_id,)
        ).fetchone()
        return self._linha_para_atendente(linha) if linha else None

    def listar_atendentes(self):
        linhas = self.conexao.execute("SELECT * FROM atendentes ORDER BY id").fetchall()
        return [self._linha_para_atendente(l) for l in linhas]

    @staticmethod
    def _linha_para_atendente(linha):
        return Atendente(linha["nome"], linha["email"], linha["setor"], linha["id"])

    # --------------------------------------------------------- tickets
    def inserir_ticket(self, ticket):
        with self.conexao:
            cursor = self.conexao.execute(
                """INSERT INTO tickets
                   (cliente_id, atendente_id, descricao, categoria, resposta_ia,
                    status, resolucao, criado_em)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (ticket.cliente_id, ticket.atendente_id, ticket.descricao,
                 ticket.categoria, ticket.resposta_ia, ticket.status,
                 ticket.resolucao, ticket.criado_em),
            )
        ticket.id = cursor.lastrowid
        return ticket.id

    def buscar_ticket(self, ticket_id):
        linha = self.conexao.execute(
            "SELECT * FROM tickets WHERE id = ?", (ticket_id,)
        ).fetchone()
        return self._linha_para_ticket(linha) if linha else None

    def listar_tickets(self, status=None):
        if status:
            linhas = self.conexao.execute(
                "SELECT * FROM tickets WHERE status = ? ORDER BY id", (status,)
            ).fetchall()
        else:
            linhas = self.conexao.execute("SELECT * FROM tickets ORDER BY id").fetchall()
        return [self._linha_para_ticket(l) for l in linhas]

    def atualizar_ticket(self, ticket):
        with self.conexao:
            cursor = self.conexao.execute(
                """UPDATE tickets
                   SET atendente_id = ?, categoria = ?, resposta_ia = ?,
                       status = ?, resolucao = ?
                   WHERE id = ?""",
                (ticket.atendente_id, ticket.categoria, ticket.resposta_ia,
                 ticket.status, ticket.resolucao, ticket.id),
            )
        return cursor.rowcount > 0

    def excluir_ticket(self, ticket_id):
        with self.conexao:
            cursor = self.conexao.execute(
                "DELETE FROM tickets WHERE id = ?", (ticket_id,)
            )
        return cursor.rowcount > 0

    @staticmethod
    def _linha_para_ticket(linha):
        return Ticket(
            cliente_id=linha["cliente_id"],
            descricao=linha["descricao"],
            categoria=linha["categoria"],
            resposta_ia=linha["resposta_ia"] or "",
            status=linha["status"],
            resolucao=linha["resolucao"] or "",
            atendente_id=linha["atendente_id"],
            criado_em=linha["criado_em"],
            id=linha["id"],
        )

    def fechar(self):
        self.conexao.close()
