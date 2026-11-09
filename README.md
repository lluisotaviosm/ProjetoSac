# SAC Automatizado — Central de Atendimento ao Cliente

Protótipo de um sistema de suporte técnico para uma provedora de internet, desenvolvido em **Python**. Os clientes abrem tickets descrevendo o problema, e uma **IA faz a triagem automática**: classifica o ticket em uma categoria e já sugere uma resposta (por exemplo, "reinicie o roteador") antes de salvá-lo no banco.

Projeto acadêmico de Ciência da Computação que integra cinco pilares: estruturas de dados, banco de dados, database application (CRUD), programação orientada a objetos e inteligência artificial.

## Funcionalidades

- Cadastro de clientes e atendentes
- Abertura de tickets com **triagem automática por IA** (categoria + resposta sugerida)
- Busca de ticket por ID usando uma **Árvore Binária de Busca (BST)**
- Listagem de todos os tickets em ordem de ID (percurso em-ordem da BST)
- Listagem de tickets por categoria usando **dicionário (tabela hash)**
- Consulta de todos os tickets de um cliente (consulta SQL pela chave estrangeira)
- Fluxo de atendimento: ticket **Aberto → Em atendimento → Resolvido**
- Exclusão de tickets
- Persistência em banco de dados **SQLite**: os dados continuam salvos ao fechar o programa

## Como os pilares aparecem no projeto

| Pilar | Implementação |
|---|---|
| Estrutura de dados | BST indexando tickets por ID (`estruturas.py`) e dicionário agrupando IDs por categoria (`servico.py`) |
| POO | `Pessoa` → `Cliente` e `Atendente` (herança), `Ticket` com encapsulamento do status e polimorfismo em `resumo()` (`modelos.py`) |
| Banco de dados | SQLite com 3 tabelas (`clientes`, `atendentes`, `tickets`), chaves primárias e estrangeiras (`banco.py`) |
| Database application | CRUD completo com consultas parametrizadas (`banco.py`, `servico.py`, `main.py`) |
| IA | Triagem via API do Google Gemini, com fallback local por palavras-chave (`ia.py`) |

## Estrutura do projeto

```
ProjetoSac/
├── main.py           # Menu de terminal (interface com o usuário)
├── servico.py        # Regras de negócio; integra banco, BST, dicionário e IA
├── banco.py          # Conexão SQLite e operações CRUD
├── modelos.py        # Classes Pessoa, Cliente, Atendente e Ticket
├── estruturas.py     # Árvore Binária de Busca
├── ia.py             # Triagem automática com IA
└── requirements.txt  # Dependências
```

Fluxo de chamadas:

```
main.py  →  servico.py  →  banco.py  →  sac.db
                 ├──────→  estruturas.py (BST)
                 └──────→  ia.py (triagem)
```

## Pré-requisitos

- Python 3.9 ou superior
- (Para a triagem com IA) uma chave de API gratuita do Google Gemini, criada em [Google AI Studio](https://aistudio.google.com/apikey)

## Instalação

```bash
git clone <URL-DO-SEU-REPOSITORIO>
cd ProjetoSac
pip install -r requirements.txt
```

## Configurando a IA

A chave da API é lida da variável de ambiente `GEMINI_API_KEY`. **Nunca coloque a chave dentro do código nem a envie ao GitHub.**

Linux / macOS:

```bash
export GEMINI_API_KEY="sua-chave"
```

Windows (cmd):

```bat
set GEMINI_API_KEY=sua-chave
```

Windows (PowerShell):

```powershell
$env:GEMINI_API_KEY="sua-chave"
```

O modelo padrão é `gemini-3.5-flash-lite`. Para usar outro, defina a variável `GEMINI_MODELO`.

**Sem chave ou sem internet?** O sistema continua funcionando: a triagem usa regras locais por palavras-chave. A tela mostra a origem da triagem em cada ticket ("IA (API Gemini)" ou "regras locais", seguido do motivo do erro).

## Como usar

```bash
python main.py
```

Menu principal:

```
 1 - Cadastrar cliente
 2 - Cadastrar atendente
 3 - Abrir ticket (triagem com IA)
 4 - Buscar ticket por ID (BST)
 5 - Listar todos os tickets (em ordem de ID)
 6 - Listar tickets por categoria (dicionário)
 7 - Assumir ticket
 8 - Resolver ticket
 9 - Excluir ticket
10 - Ver tamanho e altura da BST
11 - Listar tickets de um cliente
 0 - Sair
```

Exemplo de uso:

1. Cadastre um cliente (opção 1) e um atendente (opção 2).
2. Abra um ticket (opção 3) com o texto: `Minha internet está sem sinal e a luz vermelha do modem está acesa`.
3. O sistema classifica como **Problema Físico** e sugere reiniciar o roteador e conferir os cabos.
4. Um atendente assume (opção 7) e resolve (opção 8) o ticket.

Categorias de triagem: `Problema Físico`, `Lentidão`, `Fatura`, `Plano/Contrato` e `Outros`.

## Banco de dados

O arquivo `sac.db` é criado automaticamente na primeira execução. Modelo relacional:

```
clientes (id, nome, email UNIQUE, endereco, plano)
atendentes (id, nome, email UNIQUE, setor)
tickets (id, cliente_id → clientes, atendente_id → atendentes,
         descricao, categoria, resposta_ia, status, resolucao, criado_em)
```

Cada cliente pode ter vários tickets, e cada atendente pode resolver vários tickets (relacionamentos 1:N). Todas as consultas usam parâmetros (`?`), o que evita SQL Injection.

Para usar outro arquivo de banco, defina a variável `SAC_DB`.

## Como a BST e o dicionário funcionam

- Ao iniciar, o sistema lê os tickets do banco e monta a **BST** (chave = ID do ticket) e o **dicionário** (categoria → lista de IDs).
- A BST é montada de forma balanceada na inicialização, para evitar que IDs crescentes formem uma árvore em formato de lista.
- Toda criação, alteração ou exclusão atualiza o banco, a BST e o dicionário.

## Limitações conhecidas

- Protótipo de terminal para um único usuário (não trata acesso simultâneo).
- A BST não se auto-balanceia depois da inicialização; uma evolução natural seria usar uma árvore AVL ou rubro-negra.
- Não há autenticação de atendentes.
- A busca por categoria exige o nome exato da categoria.

## Autores

Projeto desenvolvido em grupo. **[Luis Otavio, Tiago Welsing, Guilherme Henrique, Samir Pedrosa, Macel Kristhian]**


