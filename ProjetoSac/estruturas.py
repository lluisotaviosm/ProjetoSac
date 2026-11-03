"""Estruturas de dados do SAC.

ArvoreBST: Árvore Binária de Busca indexada pelo ID do ticket.
(O dicionário / tabela hash das categorias fica em servico.py.)
"""


class NoBST:
    """Um nó da árvore: guarda a chave (ID), o valor (Ticket) e os dois filhos."""

    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.esquerda = None  # subárvore com chaves MENORES
        self.direita = None   # subárvore com chaves MAIORES


class ArvoreBST:
    def __init__(self):
        self.raiz = None
        self.tamanho = 0

    # ---------------------------------------------------------- inserir
    def inserir(self, chave, valor):
        """Desce pela árvore comparando a chave até achar o lugar vazio."""
        novo = NoBST(chave, valor)
        if self.raiz is None:
            self.raiz = novo
            self.tamanho = 1
            return

        atual = self.raiz
        while True:
            if chave == atual.chave:      # ID já existe: só troca o valor
                atual.valor = valor
                return
            if chave < atual.chave:
                if atual.esquerda is None:
                    atual.esquerda = novo
                    self.tamanho += 1
                    return
                atual = atual.esquerda
            else:
                if atual.direita is None:
                    atual.direita = novo
                    self.tamanho += 1
                    return
                atual = atual.direita

    # ----------------------------------------------------------- buscar
    def buscar(self, chave):
        """Devolve o valor da chave, ou None. A cada passo descarta metade
        (aproximadamente) da árvore: O(log n) se ela estiver balanceada."""
        atual = self.raiz
        while atual is not None:
            if chave == atual.chave:
                return atual.valor
            atual = atual.esquerda if chave < atual.chave else atual.direita
        return None

    # ---------------------------------------------------------- remover
    def remover(self, chave):
        """Remove a chave. Devolve True se removeu, False se não existia."""
        self.raiz, removido = self._remover_no(self.raiz, chave)
        if removido:
            self.tamanho -= 1
        return removido

    def _remover_no(self, no, chave):
        if no is None:
            return None, False
        if chave < no.chave:
            no.esquerda, removido = self._remover_no(no.esquerda, chave)
            return no, removido
        if chave > no.chave:
            no.direita, removido = self._remover_no(no.direita, chave)
            return no, removido

        # Achou o nó a remover. Três casos:
        if no.esquerda is None:           # 0 filhos ou só filho direito
            return no.direita, True
        if no.direita is None:            # só filho esquerdo
            return no.esquerda, True

        # 2 filhos: copia o sucessor (menor nó da direita) para cá
        # e remove o sucessor original.
        sucessor = no.direita
        while sucessor.esquerda is not None:
            sucessor = sucessor.esquerda
        no.chave, no.valor = sucessor.chave, sucessor.valor
        no.direita, _ = self._remover_no(no.direita, sucessor.chave)
        return no, True

    # --------------------------------------------------------- em ordem
    def em_ordem(self):
        """Percurso em-ordem (esquerda, nó, direita): devolve os valores
        já ORDENADOS pela chave. Versão iterativa com pilha."""
        resultado = []
        pilha = []
        atual = self.raiz
        while pilha or atual is not None:
            while atual is not None:      # desce o máximo à esquerda
                pilha.append(atual)
                atual = atual.esquerda
            atual = pilha.pop()
            resultado.append(atual.valor)
            atual = atual.direita
        return resultado

    # ------------------------------------------------------ balanceamento
    def construir_balanceada(self, itens):
        """Recebe lista de (chave, valor) JÁ ORDENADA e monta a árvore
        inserindo sempre o elemento do meio primeiro. Evita que IDs
        crescentes (1, 2, 3...) criem uma árvore torta, parecida com lista."""
        self.raiz = None
        self.tamanho = 0
        self._inserir_do_meio(itens, 0, len(itens) - 1)

    def _inserir_do_meio(self, itens, inicio, fim):
        if inicio > fim:
            return
        meio = (inicio + fim) // 2
        chave, valor = itens[meio]
        self.inserir(chave, valor)
        self._inserir_do_meio(itens, inicio, meio - 1)
        self._inserir_do_meio(itens, meio + 1, fim)

    def altura(self):
        """Número de níveis da árvore (0 se vazia)."""
        if self.raiz is None:
            return 0
        nivel = [self.raiz]
        altura = 0
        while nivel:
            altura += 1
            nivel = [filho for no in nivel
                     for filho in (no.esquerda, no.direita)
                     if filho is not None]
        return altura
