"""Classes de domínio (POO): Pessoa, Cliente, Atendente e Ticket."""

from datetime import datetime


class Pessoa:
    """Classe base: o que Cliente e Atendente têm em comum."""

    def __init__(self, nome, email, id=None):
        self.id = id
        self.nome = nome
        self.email = email

    def resumo(self):
        return f"#{self.id} {self.nome} <{self.email}>"


class Cliente(Pessoa):
    """Herda de Pessoa e acrescenta endereço e plano de internet."""

    def __init__(self, nome, email, endereco="", plano="Básico", id=None):
        super().__init__(nome, email, id)
        self.endereco = endereco
        self.plano = plano

    def resumo(self):  # polimorfismo: mesmo nome, comportamento próprio
        return f"{super().resumo()} | Plano: {self.plano}"


class Atendente(Pessoa):
    """Herda de Pessoa e acrescenta o setor de atuação."""

    def __init__(self, nome, email, setor="Suporte Técnico", id=None):
        super().__init__(nome, email, id)
        self.setor = setor

    def resumo(self):
        return f"{super().resumo()} | Setor: {self.setor}"


class Ticket:
    STATUS_VALIDOS = ("Aberto", "Em atendimento", "Resolvido")

    def __init__(self, cliente_id, descricao, categoria="Não classificado",
                 resposta_ia="", status="Aberto", resolucao="",
                 atendente_id=None, criado_em=None, id=None):
        self.id = id
        self.cliente_id = cliente_id
        self.descricao = descricao
        self.categoria = categoria
        self.resposta_ia = resposta_ia
        self.resolucao = resolucao
        self.atendente_id = atendente_id
        self.criado_em = criado_em or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._status = "Aberto"
        self.status = status  # passa pelo setter, que valida o valor

    # Encapsulamento: o status só pode receber valores válidos.
    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, novo_status):
        if novo_status not in self.STATUS_VALIDOS:
            raise ValueError(f"Status inválido: {novo_status}")
        self._status = novo_status

    # Regras de negócio ficam dentro da própria classe.
    def assumir(self, atendente_id):
        if self.status == "Resolvido":
            raise ValueError("Este ticket já foi resolvido.")
        self.atendente_id = atendente_id
        self.status = "Em atendimento"

    def resolver(self, atendente_id, resolucao):
        if not resolucao.strip():
            raise ValueError("Informe a resolução do ticket.")
        self.atendente_id = atendente_id
        self.resolucao = resolucao.strip()
        self.status = "Resolvido"

    def resumo(self):
        return f"#{self.id} [{self.status}] {self.categoria} - {self.descricao[:50]}"

    def detalhes(self):
        return (
            f"Ticket #{self.id}  ({self.criado_em})\n"
            f"Status:     {self.status}\n"
            f"Categoria:  {self.categoria}\n"
            f"Descrição:  {self.descricao}\n"
            f"Resposta automática: {self.resposta_ia or '-'}\n"
            f"Atendente:  {self.atendente_id or '-'}\n"
            f"Resolução:  {self.resolucao or '-'}"
        )
