import os
import json
import heapq
import uuid

# Configuração de diretório para salvar dados
DATA_DIR = 'data'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

CLIENTES_FILE = os.path.join(DATA_DIR, 'clientes.json')
COMPRAS_FILE = os.path.join(DATA_DIR, 'compras.json')
VOOS_FILE = os.path.join(DATA_DIR, 'voos.json')
PASSENGERS_FILE = os.path.join(DATA_DIR, 'passengers.json')

# --- PARTE 3: GRAFOS ---
class Graph:
    def __init__(self):
        self.edges = {}

    def add_flight(self, origin, dest, code, price):
        # Normaliza as strings para minúsculas para garantir consistência
        origin_lower = origin.lower()
        dest_lower = dest.lower()
        if origin_lower not in self.edges:
            self.edges[origin_lower] = []
        # Adiciona apenas a versão em minúsculas ao grafo
        self.edges[origin_lower].append((dest_lower, code, price))

    def find_best_route(self, start, end):
        # Normaliza a origem e o destino da busca para minúsculas
        start_lower = start.lower()
        end_lower = end.lower()

        # Fila de prioridade: (custo, nó atual, caminho percorrido)
        queue = [(0, start_lower, [])]

        # Dicionário para rastrear o custo mínimo para cada nó
        min_cost = {start_lower: 0}

        # Conjunto de nós já visitados (caminho finalizado)
        visited = set()

        while queue:
            cost, u, path = heapq.heappop(queue)

            # Se encontramos o destino, retornamos o caminho e o custo
            if u == end_lower:
                return path, cost

            # Se já encontramos um caminho mais curto para 'u', pulamos
            if u in visited:
                continue
            visited.add(u)

            # Explorar vizinhos
            if u in self.edges:
                for dest, code, price in self.edges[u]:
                    new_cost = cost + price
                    # Se encontramos um caminho mais barato para o vizinho
                    if dest not in min_cost or new_cost < min_cost[dest]:
                        min_cost[dest] = new_cost
                        heapq.heappush(queue, (new_cost, dest, path + [code]))

        # Se não houver caminho
        return None, float('inf')

# --- Otimização: Grafo de voos global ---
# O grafo é inicializado uma vez e atualizado apenas quando há mudanças nos voos.
flight_graph = Graph()

def atualizar_grafo_voos():
    """Limpa e recarrega o grafo de voos a partir do arquivo de voos.
    Esta função deve ser chamada na inicialização do app e sempre que um voo for adicionado, editado ou removido.
    """
    global flight_graph
    flight_graph = Graph()  # Reseta o grafo para garantir que não haja dados antigos
    voos = carregar_voos()
    for codigo, dados in voos.items():
        flight_graph.add_flight(dados['Origem'], dados['Destino'], codigo, dados['Preco'])

# --- PARTE 2: ÁRVORE B ---
class BTreeNode:
    def __init__(self, leaf=False):
        self.leaf = leaf
        self.keys = []
        self.values = []
        self.child = []

class BTree:
    def __init__(self, t):
        self.root = BTreeNode(True)
        self.t = t

    def insert(self, k, v):
        root = self.root
        if len(root.keys) == (2 * self.t) - 1:
            temp = BTreeNode()
            self.root = temp
            temp.child.insert(0, root)
            self._split_child(temp, 0)
            self._insert_non_full(temp, k, v)
        else:
            self._insert_non_full(root, k, v)

    def _insert_non_full(self, x, k, v):
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1

        # Se a chave já existe no nó atual (seja folha ou interno), atualiza o valor.
        if i < len(x.keys) and k == x.keys[i]:
            x.values[i] = v
            return

        if x.leaf:
            # Se é um nó folha e a chave não existe, insere a chave na posição correta.
            x.keys.insert(i, k)
            x.values.insert(i, v)
        else:
            # Se é um nó interno, desce para o filho apropriado.
            if len(x.child[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
                # Após a divisão, a chave pode ter subido. Verifica para qual filho descer.
                if k > x.keys[i]:
                    i += 1
            self._insert_non_full(x.child[i], k, v)

    def _split_child(self, x, i):
        t = self.t
        y = x.child[i]
        z = BTreeNode(y.leaf)
        x.child.insert(i + 1, z)
        x.keys.insert(i, y.keys[t - 1])
        x.values.insert(i, y.values[t - 1])
        z.keys = y.keys[t:(2 * t) - 1]
        z.values = y.values[t:(2 * t) - 1]
        y.keys = y.keys[0:t - 1]
        y.values = y.values[0:t - 1]
        if not y.leaf:
            z.child = y.child[t:(2 * t)]
            y.child = y.child[0:t]

    def search(self, k, x=None):
        if x is None: x = self.root
        i = 0
        while i < len(x.keys) and k > x.keys[i]:
            i += 1
        if i < len(x.keys) and k == x.keys[i]:
            return x.values[i]
        elif x.leaf:
            return None
        else:
            return self.search(k, x.child[i])

    def inorder_traversal(self, x=None, result=None):
        if result is None: result = []
        if x is None: x = self.root
        for i in range(len(x.keys)):
            if not x.leaf:
                self.inorder_traversal(x.child[i], result)
            result.append(x.values[i])
        if not x.leaf:
            self.inorder_traversal(x.child[-1], result)
        return result

# Variáveis globais
btree_cpf = BTree(3)
btree_nome = BTree(3)

def carregar_clientes():
    global btree_cpf, btree_nome
    btree_cpf = BTree(3)
    btree_nome = BTree(3)
    if os.path.exists(CLIENTES_FILE):
        try:
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
                clientes = json.load(f)

                # Agrupa todas as compras por CPF
                clientes_por_cpf = {}
                for c in clientes:
                    cpf = c['cpf']
                    if cpf not in clientes_por_cpf:
                        clientes_por_cpf[cpf] = []
                    clientes_por_cpf[cpf].append(c)
                
                # Insere a lista de compras de cada CPF na árvore B
                for cpf, records in clientes_por_cpf.items():
                    btree_cpf.insert(cpf, records)

                # A busca por nome também precisa agrupar os resultados
                clientes_por_nome = {}
                for c in clientes:
                    nome = c['nome'].lower()
                    if nome not in clientes_por_nome:
                        clientes_por_nome[nome] = []
                    clientes_por_nome[nome].append(c)
                
                for nome, records in clientes_por_nome.items():
                    btree_nome.insert(nome, records)

        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existe ou está corrompido, a aplicação continua
            # com as árvores vazias, o que é um estado válido.
            pass

def salvar_cliente(cliente):
    lista = []
    if os.path.exists(CLIENTES_FILE):
        try:
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
                lista = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existe ou está corrompido, começa com uma lista vazia.
            pass
    lista.append(cliente)
    with open(CLIENTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)
    
    # Simplificado: Busca a lista de compras (ou uma nova), adiciona a compra,
    # e usa o método 'insert' robusto que lida com criação ou atualização.
    cpf = cliente['cpf']
    records_cpf = btree_cpf.search(cpf) or []
    records_cpf.append(cliente)
    btree_cpf.insert(cpf, records_cpf)

    nome = cliente['nome'].lower()
    records_nome = btree_nome.search(nome) or []
    records_nome.append(cliente)
    btree_nome.insert(nome, records_nome)

def excluir_cliente_por_cpf(cpf):
    if not os.path.exists(CLIENTES_FILE): return False
    try:
        with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
            lista = json.load(f)
        nova_lista = [c for c in lista if str(c['cpf']) != str(cpf)]
        if len(nova_lista) == len(lista): return False
        with open(CLIENTES_FILE, 'w', encoding='utf-8') as f:
            json.dump(nova_lista, f, indent=4, ensure_ascii=False)
        
        # Após a exclusão no arquivo, recarrega as árvores B para garantir a consistência.
        # Isso recalcula os agrupamentos de compras por CPF e nome.
        carregar_clientes()
        return True
    except (FileNotFoundError, json.JSONDecodeError): return False

# Funções de acesso à memória
def get_todos_clientes():
    list_of_lists = btree_nome.inorder_traversal()
    # Achata a lista de listas em uma única lista de todas as compras
    return [compra for sublist in list_of_lists for compra in sublist]

def get_todos_clientes_por_cpf():
    """Retorna uma lista de todas as compras de clientes, ordenada por CPF em ordem decrescente."""
    list_of_lists = btree_cpf.inorder_traversal()
    # Inverte a lista de listas (que está ordenada por CPF) para obter a ordem decrescente
    # e depois achata em uma única lista de compras.
    return [compra for sublist in reversed(list_of_lists) for compra in sublist]

def buscar_cliente_por_cpf(cpf): return btree_cpf.search(cpf)
def buscar_cliente_por_nome(nome): return btree_nome.search(nome.lower())
def buscar_cliente_por_inicial(inicial):
    # Achata a lista de listas retornada e filtra
    list_of_lists = btree_nome.inorder_traversal()
    flat_list = [compra for sublist in list_of_lists for compra in sublist]
    
    # Filtra pela inicial e garante que cada registro de compra apareça
    clientes_filtrados = []
    for compra in flat_list:
        if compra['nome'].lower().startswith(inicial.lower()):
            clientes_filtrados.append(compra)
    return clientes_filtrados

def salvar_compra(compra):
    lista = []
    if os.path.exists(COMPRAS_FILE):
        try:
            with open(COMPRAS_FILE, 'r', encoding='utf-8') as f:
                lista = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existe ou está corrompido, começa com uma lista vazia.
            pass
    lista.append(compra)
    with open(COMPRAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista, f, indent=4, ensure_ascii=False)

# ATUALIZADO: Agora os voos têm campo "Data"
def carregar_voos_padrao():
    return {
        "ED100": { "Origem": "Salvador", "Destino": "São Paulo", "Milhas": 1450, "Preco": 780.50, "Aeronave": "Airbus A320", "Assentos": 180, "Data": "2025-10-25" },
        "ED202": { "Origem": "Rio de Janeiro", "Destino": "Brasília", "Milhas": 930, "Preco": 550.00, "Aeronave": "Boeing 737", "Assentos": 160, "Data": "2025-10-26" },
        "ED305": { "Origem": "São Paulo", "Destino": "Buenos Aires", "Milhas": 1690, "Preco": 1200.00, "Aeronave": "Airbus A320", "Assentos": 180, "Data": "2025-10-27" }
    }

def carregar_voos():
    if os.path.exists(VOOS_FILE):
        try:
            with open(VOOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existe ou está corrompido, carrega os voos padrão.
            return carregar_voos_padrao()
    else:
        padrao = carregar_voos_padrao()
        salvar_todos_voos(padrao)
        return padrao

def salvar_todos_voos(voos):
    with open(VOOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(voos, f, indent=4, ensure_ascii=False)

def gerar_codigo_reserva():
    return str(uuid.uuid4())[:8].upper()

def carregar_usuarios_passageiros():
    if os.path.exists(PASSENGERS_FILE):
        try:
            with open(PASSENGERS_FILE, 'r', encoding='utf-8') as f: return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Se o arquivo não existe ou está corrompido, retorna um dicionário vazio.
            return {}
    return {}

def salvar_novo_usuario(dados):
    users = carregar_usuarios_passageiros()
    if dados['email'] in users: return False
    users[dados['email']] = dados
    with open(PASSENGERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=4, ensure_ascii=False)
    return True

def buscar_usuario_por_email(email):
    return carregar_usuarios_passageiros().get(email)

carregar_clientes()
atualizar_grafo_voos() # Carrega o grafo de voos na inicialização do app