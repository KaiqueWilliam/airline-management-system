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

# --- PARTE 3: GRAFOS (Para conexões de voos) ---
class Graph:
    def __init__(self):
        self.edges = {}

    def add_flight(self, origin, dest, code, price):
        if origin not in self.edges:
            self.edges[origin] = []
        self.edges[origin].append((dest, code, price))

    def find_best_route(self, start, end):
        # Dijkstra para encontrar rota mais barata
        # Fila: (custo, cidade_atual, caminho_de_codigos)
        queue = [(0, start, [])]
        visited = set()
        min_cost = {start: 0}

        while queue:
            cost, u, path = heapq.heappop(queue)

            if u == end:
                return path, cost

            if u in visited:
                continue
            visited.add(u)

            if u in self.edges:
                for dest, code, price in self.edges[u]:
                    new_cost = cost + price
                    if dest not in min_cost or new_cost < min_cost[dest]:
                        min_cost[dest] = new_cost
                        heapq.heappush(queue, (new_cost, dest, path + [code]))
        
        return None, float('inf')

# --- PARTE 2: ÁRVORE B (Para Gestão de Clientes) ---
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
        i = len(x.keys) - 1
        if x.leaf:
            x.keys.append(None)
            x.values.append(None)
            while i >= 0 and k < x.keys[i]:
                x.keys[i + 1] = x.keys[i]
                x.values[i + 1] = x.values[i]
                i -= 1
            x.keys[i + 1] = k
            x.values[i + 1] = v
        else:
            while i >= 0 and k < x.keys[i]:
                i -= 1
            i += 1
            if len(x.child[i].keys) == (2 * self.t) - 1:
                self._split_child(x, i)
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

# Instâncias globais (Índices)
btree_cpf = BTree(3)
btree_nome = BTree(3)

# --- Funções de Arquivo (JSON) ---
def carregar_clientes():
    global btree_cpf, btree_nome
    btree_cpf = BTree(3)
    btree_nome = BTree(3)
    
    if os.path.exists(CLIENTES_FILE):
        try:
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
                clientes = json.load(f)
                for c in clientes:
                    btree_cpf.insert(c['cpf'], c)
                    btree_nome.insert(c['nome'].lower(), c)
        except (json.JSONDecodeError, ValueError):
            pass 

def salvar_cliente(cliente):
    lista_clientes = []
    if os.path.exists(CLIENTES_FILE):
        try:
            with open(CLIENTES_FILE, 'r', encoding='utf-8') as f:
                lista_clientes = json.load(f)
        except:
            lista_clientes = []
    
    lista_clientes.append(cliente)
    with open(CLIENTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista_clientes, f, indent=4, ensure_ascii=False)
    
    btree_cpf.insert(cliente['cpf'], cliente)
    btree_nome.insert(cliente['nome'].lower(), cliente)

def salvar_compra(compra_data):
    lista_compras = []
    if os.path.exists(COMPRAS_FILE):
        try:
            with open(COMPRAS_FILE, 'r', encoding='utf-8') as f:
                lista_compras = json.load(f)
        except:
            lista_compras = []
            
    lista_compras.append(compra_data)
    with open(COMPRAS_FILE, 'w', encoding='utf-8') as f:
        json.dump(lista_compras, f, indent=4, ensure_ascii=False)

def carregar_voos_padrao():
    return {
        "ED100": { "Origem": "Salvador", "Destino": "São Paulo", "Milhas": 1450, "Preco": 780.50, "Aeronave": "Airbus A320", "Assentos": 180 },
        "ED202": { "Origem": "Rio de Janeiro", "Destino": "Brasília", "Milhas": 930, "Preco": 550.00, "Aeronave": "Boeing 737", "Assentos": 160 },
        "ED305": { "Origem": "São Paulo", "Destino": "Buenos Aires", "Milhas": 1690, "Preco": 1200.00, "Aeronave": "Airbus A320", "Assentos": 180 }
    }

def carregar_voos():
    if os.path.exists(VOOS_FILE):
        try:
            with open(VOOS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return carregar_voos_padrao()
    else:
        padrao = carregar_voos_padrao()
        salvar_todos_voos(padrao)
        return padrao

def salvar_todos_voos(voos_dict):
    with open(VOOS_FILE, 'w', encoding='utf-8') as f:
        json.dump(voos_dict, f, indent=4, ensure_ascii=False)

def gerar_codigo_reserva():
    return str(uuid.uuid4())[:8].upper()

# Inicializa índices ao rodar
carregar_clientes()