"""Triagem automática do ticket com IA.

Fluxo: o texto do cliente vai para a API do Google Gemini, que devolve a
categoria e uma resposta automática. Se a API não estiver disponível (sem
chave, sem internet, erro), o sistema usa regras locais por palavra-chave,
para nunca travar a abertura do ticket.
"""

import json
import os
import unicodedata

import requests

CATEGORIAS = ("Problema Físico", "Lentidão", "Fatura", "Plano/Contrato", "Outros")

URL_API = "https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent"
MODELO = os.environ.get("GEMINI_MODELO", "gemini-3.5-flash-lite")

INSTRUCAO = (
    "Você é o assistente de suporte de uma provedora de internet. "
    "Receba o relato do cliente e responda SOMENTE com um JSON no formato "
    '{"categoria": "...", "resposta": "..."}. '
    "A categoria deve ser exatamente uma de: " + ", ".join(CATEGORIAS) + ". "
    "A resposta deve ser curta, educada, em português, com passos simples "
    "para tentar resolver (ex.: reiniciar o roteador, conferir cabos). "
    "Se não houver solução simples, diga que o ticket será encaminhado a um atendente."
)

# Tabela hash (dicionário): categoria -> palavras-chave (sem acento, minúsculas).
PALAVRAS_CHAVE = {
    "Problema Físico": ["luz vermelha", "luz piscando", "cabo", "roteador", "modem",
                        "fibra", "sem internet", "sem sinal", "nao liga", "queda",
                        "caiu", "desconecta", "equipamento"],
    "Lentidão": ["lento", "lenta", "lentidao", "devagar", "travando", "trava",
                 "velocidade", "oscila", "instavel"],
    "Fatura": ["fatura", "boleto", "cobranca", "cobrado", "pagamento",
               "segunda via", "vencimento", "paguei", "debito"],
    "Plano/Contrato": ["plano", "contrato", "upgrade", "cancelar", "cancelamento",
                       "mudanca de endereco", "titularidade", "contratar"],
}

RESPOSTAS_PADRAO = {
    "Problema Físico": "Desligue o roteador da tomada por 30 segundos e ligue novamente. "
                       "Confira se os cabos estão bem encaixados. Se a luz vermelha "
                       "continuar acesa, um atendente vai agendar uma visita técnica.",
    "Lentidão": "Reinicie o roteador e aproxime o aparelho dele para testar. "
                "Se possível, teste com cabo de rede. Se a lentidão continuar, "
                "um atendente vai analisar sua conexão.",
    "Fatura": "Sua solicitação sobre a fatura foi registrada. "
              "Um atendente financeiro vai verificar e retornar em breve.",
    "Plano/Contrato": "Sua solicitação sobre plano ou contrato foi registrada. "
                      "Um atendente comercial entrará em contato.",
    "Outros": "Recebemos seu relato e ele será encaminhado a um atendente.",
}


def _normalizar(texto):
    """Minúsculas e sem acentos, para comparar palavras-chave."""
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn").lower()


def _triagem_local(descricao):
    """Plano B: conta quantas palavras-chave de cada categoria aparecem."""
    texto = _normalizar(descricao)
    melhor_categoria, melhor_pontos = "Outros", 0
    for categoria, palavras in PALAVRAS_CHAVE.items():
        pontos = sum(1 for p in palavras if p in texto)
        if pontos > melhor_pontos:
            melhor_categoria, melhor_pontos = categoria, pontos
    return melhor_categoria, RESPOSTAS_PADRAO[melhor_categoria]


def _mensagem_erro(resposta):
    """Pega o motivo do erro que a API devolveu (ex.: chave inválida)."""
    try:
        return resposta.json()["error"]["message"][:150]
    except Exception:
        return resposta.text[:150]


def _triagem_com_api(descricao):
    """Plano A: chama a API do Gemini. Qualquer falha vira exceção."""
    chave = os.environ.get("GEMINI_API_KEY")
    if not chave:
        raise RuntimeError("GEMINI_API_KEY não definida")

    resposta = requests.post(
        URL_API.format(modelo=MODELO),
        headers={
            "x-goog-api-key": chave,  # a chave vai no cabeçalho, não na URL
            "content-type": "application/json",
        },
        json={
            # instrução do sistema: o "papel" da IA
            "system_instruction": {"parts": [{"text": INSTRUCAO}]},
            # mensagem do usuário: o relato do cliente
            "contents": [{"role": "user", "parts": [{"text": descricao}]}],
            "generationConfig": {
                "responseMimeType": "application/json",  # pede a resposta em JSON
                "temperature": 0.2,                      # respostas mais estáveis
                "maxOutputTokens": 1024,
            },
        },
        timeout=30,
    )
    if resposta.status_code != 200:
        raise RuntimeError(f"erro {resposta.status_code}: {_mensagem_erro(resposta)}")

    partes = resposta.json()["candidates"][0]["content"]["parts"]
    texto = "".join(p.get("text", "") for p in partes if not p.get("thought"))
    dados = json.loads(texto[texto.find("{"): texto.rfind("}") + 1])

    categoria = dados.get("categoria", "Outros")
    if categoria not in CATEGORIAS:  # nunca confiar cegamente na saída da IA
        categoria = "Outros"
    texto_resposta = str(dados.get("resposta", "")).strip()
    if not texto_resposta:
        raise ValueError("A IA devolveu resposta vazia")
    return categoria, texto_resposta


def triar_ticket(descricao):
    """Devolve (categoria, resposta_automatica, origem)."""
    try:
        categoria, resposta = _triagem_com_api(descricao)
        return categoria, resposta, "IA (API Gemini)"
    except Exception as erro:  # sem chave, sem internet, JSON inválido...
        categoria, resposta = _triagem_local(descricao)
        return categoria, resposta, f"regras locais ({erro})"