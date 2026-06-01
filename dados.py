import json
import os

PASTA = 'data'
ARQ_ATIVOS = os.path.join(PASTA, 'ativos.json')
ARQ_VULNS = os.path.join(PASTA, 'vulns.json')

def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

def carregar_json(caminho):
    try:
        with open(caminho, encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return {}

def criar_arquivo(caminho):
    if not os.path.exists(caminho):
        salvar_json(caminho, {})

def inicializar():
    os.makedirs(PASTA, exist_ok=True)
    criar_arquivo(ARQ_ATIVOS)
    criar_arquivo(ARQ_VULNS)

def carregar_ativos():
    return carregar_json(ARQ_ATIVOS)

def salvar_ativos(ativos):
    salvar_json(ARQ_ATIVOS, ativos)

def carregar_vulns():
    return carregar_json(ARQ_VULNS)

def salvar_vulns(vulns):
    salvar_json(ARQ_VULNS, vulns)
