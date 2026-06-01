import json, os

PASTA      = 'data'
ARQ_ATIVOS = os.path.join(PASTA, 'ativos.json')
ARQ_VULNS  = os.path.join(PASTA, 'vulns.json')

def inicializar():
    os.makedirs(PASTA, exist_ok=True)
    for arq in (ARQ_ATIVOS, ARQ_VULNS):
        if not os.path.exists(arq):
            with open(arq, 'w', encoding='utf-8') as f:
                json.dump({}, f)

def carregar_ativos():
    try:
        with open(ARQ_ATIVOS, encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def salvar_ativos(ativos):
    with open(ARQ_ATIVOS, 'w', encoding='utf-8') as f:
        json.dump(ativos, f, ensure_ascii=False, indent=2)

def carregar_vulns():
    try:
        with open(ARQ_VULNS, encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def salvar_vulns(vulns):
    with open(ARQ_VULNS, 'w', encoding='utf-8') as f:
        json.dump(vulns, f, ensure_ascii=False, indent=2)