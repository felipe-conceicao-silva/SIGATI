from enum import Enum

class TipoAtivo(Enum):
    NOTEBOOK            = 1
    SERVIDOR            = 2
    ROTEADOR            = 3
    SOFTWARE_LICENCIADO = 4
    APLICACAO_WEB       = 5
    BANCO_DE_DADOS      = 6
    IMPRESSORA_REDE     = 7
    ESTACAO_TRABALHO    = 8

class Severidade(Enum):
    BAIXA   = 1
    MEDIA   = 2
    ALTA    = 3
    CRITICA = 4

class StatusVuln(Enum):
    ABERTA            = 1
    EM_TRATAMENTO     = 2
    CORRIGIDA         = 3
    ACEITA_COMO_RISCO = 4