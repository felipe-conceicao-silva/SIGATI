import os, sys
from tipos import TipoAtivo, Severidade, StatusVuln
from dados import inicializar, carregar_ativos, salvar_ativos, carregar_vulns, salvar_vulns

ativos   = {} 
por_nome = {} 
vulns    = {}

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
            v = int(input(prompt).strip())
            if minimo is not None and v < minimo:
                print(f'  [!] Valor mínimo: {minimo}.')
                continue
            if maximo is not None and v > maximo:
                print(f'  [!] Valor máximo: {maximo}.')
                continue
            return v
        except ValueError:
            print('  Digite um número inteiro.')

def ler_texto(prompt, obrigatorio=True):
    while True:
        v = input(prompt).strip()
        if obrigatorio and not v:
            print('  [!] Campo obrigatório.')
            continue
        return v

def escolher(enum_cls, rotulo):
    print()
    print(f'  {rotulo}:')
    for item in enum_cls:
        nome = item.name.replace('_', ' ').title()
        print(f'    {item.value}  →  {nome}')
    return ler_inteiro('  Opção: ', minimo=1, maximo=len(enum_cls))

def nome_enum(enum_cls, valor):
    try:
        return enum_cls(int(valor)).name.replace('_', ' ').title()
    except Exception:
        return str(valor)

def proximo_id(dic):
    return max((int(k) for k in dic), default=0) + 1
    
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
    print('  [!] Ativo não encontrado.')
    return None, None

def exibir_ativo(d):
    desc = d.get('descricao') or '—'
    qtd  = len(d.get('vulnerabilidades', []))
    print()
    print(f"  ID          : {d['id']}")
    print(f"  Hostname    : {d['hostname']}")
    print(f"  Responsável : {d['responsavel']}")
    print(f"  Setor       : {d['setor']}")
    print(f"  Tipo        : {nome_enum(TipoAtivo, d['tipo'])}")
    print(f"  Descrição   : {desc}")
    print(f"  Vulns       : {qtd}")

def exibir_vuln(v):
    print('  ' + '─' * 50)
    print(f"  ID         : {v['id']}")
    print(f"  Descrição  : {v['descricao']}")
    print(f"  Categoria  : {v['categoria']}")
    print(f"  Severidade : {nome_enum(Severidade, v['severidade'])}")
    print(f"  Status     : {nome_enum(StatusVuln, v['status'])}")
    
def cadastrar_ativo():
    titulo('Cadastrar Ativo de TI')
    while True:
        novo_id = ler_inteiro('  ID do ativo (inteiro único): ', minimo=1)
        if str(novo_id) not in ativos:
            break
        print(f'  [!] ID {novo_id} já está em uso.')
    while True:
        hostname = ler_texto('  Nome / Hostname: ')
        if hostname.lower() not in por_nome:
            break
        print('  [!] Hostname já cadastrado.')
    responsavel = ler_texto('  Responsável: ')
    setor       = ler_texto('  Setor / Localização: ')
    tipo        = escolher(TipoAtivo, 'Tipo do ativo')
    descricao   = ler_texto('  Descrição (Enter para pular): ', obrigatorio=False)
    id_str = str(novo_id)
    ativos[id_str] = {
        'id': novo_id, 'hostname': hostname, 'responsavel': responsavel,
        'setor': setor, 'tipo': tipo, 'descricao': descricao,
        'vulnerabilidades': [],
    }
    por_nome[hostname.lower()] = id_str
    salvar_ativos(ativos)
    print(f'Ativo cadastrado (ID: {novo_id}).')
    pausar()

def consultar_ativo():
    titulo('Consultar Ativo de TI')
    _, dados = buscar_ativo()
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
    for k in sorted(ativos, key=lambda x: int(x)):
        d = ativos[k]
        tipo = nome_enum(TipoAtivo, d['tipo'])
        print(f"  {d['id']:<6} {d['hostname']:<22} {d['responsavel']:<20} {tipo}")
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
    resp_atual  = dados['responsavel']
    setor_atual = dados['setor']
    desc_atual  = dados.get('descricao') or '—'
    novo_resp  = ler_texto(f'  Responsável [{resp_atual}]: ', obrigatorio=False)
    novo_setor = ler_texto(f'  Setor [{setor_atual}]: ', obrigatorio=False)
    nova_desc  = ler_texto(f'  Descrição [{desc_atual}]: ', obrigatorio=False)
    tipo_atual = nome_enum(TipoAtivo, dados['tipo'])
    print(f'  Tipo atual: {tipo_atual}')
    if ler_texto('  Alterar tipo? (s/N): ', obrigatorio=False).lower() == 's':
        dados['tipo'] = escolher(TipoAtivo, 'Novo tipo')
    if novo_resp:  dados['responsavel'] = novo_resp
    if novo_setor: dados['setor']       = novo_setor
    if nova_desc:  dados['descricao']   = nova_desc
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
    print('  [✓] Ativo e vulnerabilidades removidos.')
    pausar()

def cadastrar_vuln():
    titulo('Cadastrar Vulnerabilidade')
    id_str, ativo = buscar_ativo()
    if not ativo:
        pausar()
        return
    print(f"  Ativo: {ativo['hostname']} (ID {ativo['id']})")
    descricao  = ler_texto('  Descrição da vulnerabilidade: ')
    categoria  = ler_texto('  Categoria: ')
    severidade = escolher(Severidade, 'Severidade')
    status     = escolher(StatusVuln, 'Status')
    novo_id = proximo_id(vulns)
    vulns[str(novo_id)] = {
        'id': novo_id, 'ativo_id': ativo['id'],
        'descricao': descricao, 'categoria': categoria,
        'severidade': severidade, 'status': status,
    }
    ativo.setdefault('vulnerabilidades', []).append(novo_id)
    ativos[id_str] = ativo
    salvar_vulns(vulns)
    salvar_ativos(ativos)
    print(f' Vulnerabilidade cadastrada (ID: {novo_id}).')
    pausar()

def ver_vulns():
    titulo('Vulnerabilidades do Ativo')
    _, ativo = buscar_ativo()
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
            v = vulns.get(str(vid))
            if v:
                exibir_vuln(v)
    pausar()

def atualizar_vuln():
    titulo('Atualizar Vulnerabilidade')
    id_str, ativo = buscar_ativo()
    if not ativo:
        pausar()
        return
    ids = ativo.get('vulnerabilidades', [])
    if not ids:
        print('  [i] Nenhuma vulnerabilidade para este ativo.')
        pausar()
        return
    print(f"  Vulnerabilidades de '{ativo['hostname']}':")
    print('  ' + '─' * 55)
    for vid in ids:
        v = vulns.get(str(vid))
        if v:
            sev  = nome_enum(Severidade, v['severidade'])
            sts  = nome_enum(StatusVuln, v['status'])
            desc = v['descricao'][:45]
            print(f"  [{v['id']:>3}]  {desc:<46}  {sev:<8}  {sts}")
    vid_sel = ler_inteiro('  ID da vulnerabilidade: ', minimo=1)
    v = vulns.get(str(vid_sel))
    if not v or vid_sel not in ids:
        print('Vulnerabilidade não encontrada para este ativo.')
        pausar()
        return
    print(f"  Vulnerabilidade: {v['descricao']}")
    if ler_texto('  Alterar status? (s/N): ', obrigatorio=False).lower() == 's':
        v['status'] = escolher(StatusVuln, 'Novo status')
    if ler_texto('  Alterar severidade? (s/N): ', obrigatorio=False).lower() == 's':
        v['severidade'] = escolher(Severidade, 'Nova severidade')
    vulns[str(vid_sel)] = v
    salvar_vulns(vulns)
    print('Vulnerabilidade atualizada.')
    pausar()
    
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

ACOES = {
    1: cadastrar_ativo, 2: consultar_ativo, 3: atualizar_ativo, 4: remover_ativo,   5: listar_ativos,
    6: cadastrar_vuln,  7: ver_vulns,       8: atualizar_vuln,
}

def main():
    global ativos, por_nome, vulns
    inicializar()
    ativos   = carregar_ativos()
    por_nome = {d['hostname'].lower(): k for k, d in ativos.items()}
    vulns    = carregar_vulns()
    while True:
        limpar()
        menu()
        op = ler_inteiro('  Selecione uma opção: ', minimo=0, maximo=8)
        if op == 0:
            print('  Encerrando.')
            sys.exit(0)
        ACOES[op]()

if __name__ == '__main__':
    main()