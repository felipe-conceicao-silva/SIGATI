TIPOS_ATIVO = {
    1: 'Notebook',
    2: 'Servidor',
    3: 'Roteador',
    4: 'Software Licenciado',
    5: 'Aplicacao Web',
    6: 'Banco De Dados',
    7: 'Impressora Rede',
    8: 'Estacao Trabalho',
}

SEVERIDADES = {
    1: 'Baixa',
    2: 'Media',
    3: 'Alta',
    4: 'Critica',
}

STATUS_VULN = {
    1: 'Aberta',
    2: 'Em Tratamento',
    3: 'Corrigida',
    4: 'Aceita Como Risco',
}

def nome_opcao(opcoes, valor):
    try:
        return opcoes[int(valor)]
    except (KeyError, TypeError, ValueError):
        return str(valor)
