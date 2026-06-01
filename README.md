---
jupyter:
  jupytext:
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
  kernelspec:
    display_name: Python D
    language: python
    name: python3
---

# SIGATI - Sistema de Gestão de Ativos de TI

## Arquivo `tipos.py`

Neste arquivo deixei os valores fixos do sistema. Troquei as enumerações por dicionários simples, porque essa estrutura é suficiente para relacionar cada código ao texto exibido no programa, antes tava uma coisa muito complicada usando enum.

```python
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
```

Depois criei uma função pequena para transformar o código salvo no JSON em texto. Assim, as telas não precisam repetir essa conversão,

```python
def nome_opcao(opcoes, valor):
    try:
        return opcoes[int(valor)]
    except (KeyError, TypeError, ValueError):
        return str(valor)
```

## Arquivo `dados.py`

Em dados eu concentrei a leitura e a gravação dos arquivos. Tambem mantive o uso de JSON porque ele é direto e facilita a conferência dos dados salvos.

```python
import json
import os

PASTA = 'data'
ARQ_ATIVOS = os.path.join(PASTA, 'ativos.json')
ARQ_VULNS = os.path.join(PASTA, 'vulns.json')
```

Separei as funções de salvar e carregar. Com isso ativos e vulnerabilidades usam a mesma lógica de arquivo.

```python
def salvar_json(caminho, dados):
    with open(caminho, 'w', encoding='utf-8') as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)

def carregar_json(caminho):
    try:
        with open(caminho, encoding='utf-8') as arquivo:
            return json.load(arquivo)
    except (OSError, json.JSONDecodeError):
        return {}
```

Também mantive a criação automática da pasta e dos arquivos para evita erro na primeira execução do programa.

```python
def criar_arquivo(caminho):
    if not os.path.exists(caminho):
        salvar_json(caminho, {})

def inicializar():
    os.makedirs(PASTA, exist_ok=True)
    criar_arquivo(ARQ_ATIVOS)
    criar_arquivo(ARQ_VULNS)
```

No final, deixei funções específicas para ativos e vulnerabilidades. Elas deixam o restante do código mais legível.

```python
def carregar_ativos():
    return carregar_json(ARQ_ATIVOS)

def salvar_ativos(ativos):
    salvar_json(ARQ_ATIVOS, ativos)

def carregar_vulns():
    return carregar_json(ARQ_VULNS)

def salvar_vulns(vulns):
    salvar_json(ARQ_VULNS, vulns)
```

## Arquivo `operacoes.py`

Criei este arquivo para tirar as operações do `main.py`. Aqui ficam os dados carregados, as funções de tela, as buscas, os cadastros e o menu, antes o main tava enorme, então modularizei um pouco.

```python
import os

from dados import carregar_ativos, carregar_vulns, inicializar, salvar_ativos, salvar_vulns
from tipos import SEVERIDADES, STATUS_VULN, TIPOS_ATIVO, nome_opcao

ativos = {}
por_nome = {}
vulns = {}
```

Comecei pelo carregamento do sistema. Montei também um índice por hostname para manter a busca pelo nome sem percorrer todos os ativos a cada consulta.

```python
def carregar_sistema():
    global ativos, por_nome, vulns
    inicializar()
    ativos = carregar_ativos()
    vulns = carregar_vulns()
    por_nome = montar_indice_nomes()

def montar_indice_nomes():
    indice = {}
    for id_str, ativo in ativos.items():
        indice[ativo['hostname'].lower()] = id_str
    return indice
```

Depois organizei a tela e entrada de dados com funções simples para validar número, texto e escolha de opções.

```python
def limpar():
    os.system('cls' if os.name == 'nt' else 'clear')

def titulo(texto):
    print()
    print('═' * 56)
    print(f'  {texto}')
    print('═' * 56)

def pausar():
    print()
    input('  Pressione Enter para continuar')

def ler_inteiro(prompt, minimo=None, maximo=None):
    while True:
        try:
            valor = int(input(prompt).strip())
            if minimo is not None and valor < minimo:
                print(f'  Valor mínimo: {minimo}.')
                continue
            if maximo is not None and valor > maximo:
                print(f'  Valor máximo: {maximo}.')
                continue
            return valor
        except ValueError:
            print('  Digite um número inteiro.')

def ler_texto(prompt, obrigatorio=True):
    while True:
        valor = input(prompt).strip()
        if obrigatorio and not valor:
            print('  Campo obrigatório.')
            continue
        return valor

def escolher(opcoes, rotulo):
    print()
    print(f'  {rotulo}:')
    for codigo in opcoes:
        print(f'    {codigo}  ->  {opcoes[codigo]}')
    return ler_inteiro('  Opção: ', minimo=1, maximo=len(opcoes))
```

Separei as funções usadas por várias operações. Elas localizam registros e exibem as informações em um formato único.

```python
def proximo_id(dic):
    maior = 0
    for chave in dic:
        if int(chave) > maior:
            maior = int(chave)
    return maior + 1

def buscar_ativo():
    print()
    print('  Buscar por:  1 ID    2 Hostname')
    op = ler_inteiro('  Opção: ', minimo=1, maximo=2)
    if op == 1:
        id_str = str(ler_inteiro('  ID do ativo: ', minimo=1))
        if id_str in ativos:
            return id_str, ativos[id_str]
    else:
        nome = ler_texto('  Hostname: ').lower()
        if nome in por_nome:
            id_str = por_nome[nome]
            return id_str, ativos[id_str]
    print('  Ativo não encontrado.')
    return None, None

def exibir_ativo(dados):
    desc = dados.get('descricao') or '—'
    qtd = len(dados.get('vulnerabilidades', []))
    print()
    print(f"  ID          : {dados['id']}")
    print(f"  Hostname    : {dados['hostname']}")
    print(f"  Responsável : {dados['responsavel']}")
    print(f"  Setor       : {dados['setor']}")
    print(f"  Tipo        : {nome_opcao(TIPOS_ATIVO, dados['tipo'])}")
    print(f"  Descrição   : {desc}")
    print(f"  Vulns       : {qtd}")

def exibir_vuln(vuln):
    print('  ' + '─' * 50)
    print(f"  ID         : {vuln['id']}")
    print(f"  Descrição  : {vuln['descricao']}")
    print(f"  Categoria  : {vuln['categoria']}")
    print(f"  Severidade : {nome_opcao(SEVERIDADES, vuln['severidade'])}")
    print(f"  Status     : {nome_opcao(STATUS_VULN, vuln['status'])}")
```

Para cadastrar ativo, tirei a validação de ID e hostname. Assim, a função de cadastro ficou mais curta.

```python
def ler_id_ativo_novo():
    while True:
        novo_id = ler_inteiro('  ID do ativo (inteiro único): ', minimo=1)
        if str(novo_id) not in ativos:
            return novo_id
        print(f'  ID {novo_id} já está em uso.')

def ler_hostname_novo():
    while True:
        hostname = ler_texto('  Nome / Hostname: ')
        if hostname.lower() not in por_nome:
            return hostname
        print('  Hostname já cadastrado.')

def cadastrar_ativo():
    titulo('Cadastrar Ativo de TI')
    novo_id = ler_id_ativo_novo()
    hostname = ler_hostname_novo()
    responsavel = ler_texto('  Responsável: ')
    setor = ler_texto('  Setor / Localização: ')
    tipo = escolher(TIPOS_ATIVO, 'Tipo do ativo')
    descricao = ler_texto('  Descrição (Enter para pular): ', obrigatorio=False)
    id_str = str(novo_id)
    ativos[id_str] = {
        'id': novo_id,
        'hostname': hostname,
        'responsavel': responsavel,
        'setor': setor,
        'tipo': tipo,
        'descricao': descricao,
        'vulnerabilidades': [],
    }
    por_nome[hostname.lower()] = id_str
    salvar_ativos(ativos)
    print(f'Ativo cadastrado (ID: {novo_id}).')
    pausar()
```

Depois eu organizei as demais operações de ativo. Mantive as mesmas regras de consulta, listagem, atualização e remoção.

```python
def consultar_ativo():
    titulo('Consultar Ativo de TI')
    id_str, dados = buscar_ativo()
    if dados:
        exibir_ativo(dados)
    pausar()

def listar_ativos():
    titulo('Listar Todos os Ativos')
    if not ativos:
        print('  Nenhum ativo cadastrado.')
        pausar()
        return
    print()
    print(f"  {'ID':<6} {'Hostname':<22} {'Responsável':<20} Tipo")
    print('  ' + '─' * 55)
    ids = list(ativos)
    ids.sort(key=int)
    for id_str in ids:
        ativo = ativos[id_str]
        tipo = nome_opcao(TIPOS_ATIVO, ativo['tipo'])
        print(f"  {ativo['id']:<6} {ativo['hostname']:<22} {ativo['responsavel']:<20} {tipo}")
    print()
    print(f"  Total: {len(ativos)} ativo(s)")
    pausar()

def atualizar_ativo():
    titulo('Atualizar Ativo de TI')
    id_str, dados = buscar_ativo()
    if not dados:
        pausar()
        return
    print(f"  Editando: {dados['hostname']} (ID {dados['id']})")
    print('  [ Enter sem digitar = manter valor atual ]')
    resp_atual = dados['responsavel']
    setor_atual = dados['setor']
    desc_atual = dados.get('descricao') or '—'
    novo_resp = ler_texto(f'  Responsável [{resp_atual}]: ', obrigatorio=False)
    novo_setor = ler_texto(f'  Setor [{setor_atual}]: ', obrigatorio=False)
    nova_desc = ler_texto(f'  Descrição [{desc_atual}]: ', obrigatorio=False)
    tipo_atual = nome_opcao(TIPOS_ATIVO, dados['tipo'])
    print(f'  Tipo atual: {tipo_atual}')
    if ler_texto('  Alterar tipo? (s/N): ', obrigatorio=False).lower() == 's':
        dados['tipo'] = escolher(TIPOS_ATIVO, 'Novo tipo')
    if novo_resp:
        dados['responsavel'] = novo_resp
    if novo_setor:
        dados['setor'] = novo_setor
    if nova_desc:
        dados['descricao'] = nova_desc
    ativos[id_str] = dados
    salvar_ativos(ativos)
    print('  [✓] Ativo atualizado.')
    pausar()

def remover_ativo():
    titulo('Remover Ativo de TI')
    id_str, dados = buscar_ativo()
    if not dados:
        pausar()
        return
    qtd = len(dados.get('vulnerabilidades', []))
    print(f"  Ativo: {dados['hostname']} (ID {dados['id']})")
    if qtd:
        print(f'  [!] {qtd} vulnerabilidade(s) associada(s) também será(ão) removida(s).')
    if ler_texto('  Confirmar remoção? (s/N): ', obrigatorio=False).lower() != 's':
        print('  Operação cancelada.')
        pausar()
        return
    for vid in dados.get('vulnerabilidades', []):
        vulns.pop(str(vid), None)
    por_nome.pop(dados['hostname'].lower(), None)
    del ativos[id_str]
    salvar_ativos(ativos)
    salvar_vulns(vulns)
    print('  Ativo e vulnerabilidades removidos.')
    pausar()
```

Mantive as operações de vulnerabilidade. Elas continuam vinculadas ao ativo selecionado antes de qualquer alteração.

```python
def cadastrar_vuln():
    titulo('Cadastrar Vulnerabilidade')
    id_str, ativo = buscar_ativo()
    if not ativo:
        pausar()
        return
    print(f"  Ativo: {ativo['hostname']} (ID {ativo['id']})")
    descricao = ler_texto('  Descrição da vulnerabilidade: ')
    categoria = ler_texto('  Categoria: ')
    severidade = escolher(SEVERIDADES, 'Severidade')
    status = escolher(STATUS_VULN, 'Status')
    novo_id = proximo_id(vulns)
    vulns[str(novo_id)] = {
        'id': novo_id,
        'ativo_id': ativo['id'],
        'descricao': descricao,
        'categoria': categoria,
        'severidade': severidade,
        'status': status,
    }
    ativo.setdefault('vulnerabilidades', []).append(novo_id)
    ativos[id_str] = ativo
    salvar_vulns(vulns)
    salvar_ativos(ativos)
    print(f' Vulnerabilidade cadastrada (ID: {novo_id}).')
    pausar()

def ver_vulns():
    titulo('Vulnerabilidades do Ativo')
    id_str, ativo = buscar_ativo()
    if not ativo:
        pausar()
        return
    print(f"  Ativo: {ativo['hostname']} (ID {ativo['id']})")
    ids = ativo.get('vulnerabilidades', [])
    if not ids:
        print(' Nenhuma vulnerabilidade registrada para este ativo.')
    else:
        print(f'  Total: {len(ids)} vulnerabilidade(s)')
        for vid in ids:
            vuln = vulns.get(str(vid))
            if vuln:
                exibir_vuln(vuln)
    pausar()
```

Separei a listagem resumida. Isso evita deixar a função principal dessa etapa muito grande.

```python
def mostrar_resumo_vulns(ativo):
    print(f"  Vulnerabilidades de '{ativo['hostname']}':")
    print('  ' + '─' * 55)
    for vid in ativo.get('vulnerabilidades', []):
        vuln = vulns.get(str(vid))
        if vuln:
            severidade = nome_opcao(SEVERIDADES, vuln['severidade'])
            status = nome_opcao(STATUS_VULN, vuln['status'])
            desc = vuln['descricao'][:45]
            print(f"  [{vuln['id']:>3}]  {desc:<46}  {severidade:<8}  {status}")

def atualizar_vuln():
    titulo('Atualizar Vulnerabilidade')
    id_str, ativo = buscar_ativo()
    if not ativo:
        pausar()
        return
    ids = ativo.get('vulnerabilidades', [])
    if not ids:
        print('  Nenhuma vulnerabilidade para este ativo.')
        pausar()
        return
    mostrar_resumo_vulns(ativo)
    vid_sel = ler_inteiro('  ID da vulnerabilidade: ', minimo=1)
    vuln = vulns.get(str(vid_sel))
    if not vuln or vid_sel not in ids:
        print('Vulnerabilidade não encontrada para este ativo.')
        pausar()
        return
    print(f"  Vulnerabilidade: {vuln['descricao']}")
    if ler_texto('  Alterar status? (s/N): ', obrigatorio=False).lower() == 's':
        vuln['status'] = escolher(STATUS_VULN, 'Novo status')
    if ler_texto('  Alterar severidade? (s/N): ', obrigatorio=False).lower() == 's':
        vuln['severidade'] = escolher(SEVERIDADES, 'Nova severidade')
    vulns[str(vid_sel)] = vuln
    salvar_vulns(vulns)
    print('Vulnerabilidade atualizada.')
    pausar()
```

Deixei o menu e o laço principal neste arquivo. Usei `if` e `elif` para deixar a escolha das opções mais fácil de distinguir.

```python
def menu():
    print("""
        SIGATI — Sistema de Gestão de Ativos de TI
        
        ATIVOS
        1 - Cadastrar ativo
        2 - Consultar ativo
        3 - Atualizar ativo
        4 - Remover ativo
        5 - Listar ativos
        
        VULNERABILIDADES
        6 - Cadastrar vulnerabilidade
        7 - Visualizar vulnerabilidades
        8 - Atualizar vulnerabilidade
        
        0 - Sair
    """)

def executar_opcao(op):
    if op == 1:
        cadastrar_ativo()
    elif op == 2:
        consultar_ativo()
    elif op == 3:
        atualizar_ativo()
    elif op == 4:
        remover_ativo()
    elif op == 5:
        listar_ativos()
    elif op == 6:
        cadastrar_vuln()
    elif op == 7:
        ver_vulns()
    elif op == 8:
        atualizar_vuln()

def executar_sistema():
    while True:
        limpar()
        menu()
        op = ler_inteiro('  Selecione uma opção: ', minimo=0, maximo=8)
        if op == 0:
            print('  Encerrando.')
            break
        executar_opcao(op)
```

## Arquivo `main.py`

Deixei o `main.py` somente como ponto de entrada. Ele carrega os dados e inicia o menu, sem misturar as regras do sistema com a inicialização.

```python
from operacoes import carregar_sistema, executar_sistema

def main():
    carregar_sistema()
    executar_sistema()

if __name__ == '__main__':
    main()
```
