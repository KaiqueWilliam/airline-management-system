import json
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..structures import (
    carregar_voos, salvar_todos_voos,
    excluir_cliente_por_cpf, get_todos_clientes, get_todos_clientes_por_cpf,
    buscar_cliente_por_cpf, buscar_cliente_por_nome, buscar_cliente_por_inicial, atualizar_grafo_voos
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

# --- Melhoria de Segurança: Carregar senhas de um arquivo e usar hash ---
ADMIN_USERS_FILE = os.path.join('data', 'admins.json')

def load_admin_users():
    """Carrega usuários admin de um arquivo JSON, com senhas hasheadas."""
    if not os.path.exists(ADMIN_USERS_FILE):
        # Cria um admin padrão se o arquivo não existir.
        default_admins = { "admin": { "password": generate_password_hash("1234") } }
        with open(ADMIN_USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_admins, f, indent=4)
        return default_admins
    
    with open(ADMIN_USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

admin_users = load_admin_users()

@admin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = admin_users.get(request.form['username'])
        if user and check_password_hash(user['password'], request.form['password']):
            session['logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        flash('Login inválido.', 'danger')
    return render_template('admin/admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    return render_template('admin/admin_dashboard.html', voos=carregar_voos())

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@admin_bp.route('/voo/add', methods=['POST'])
def add_voo():
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    voos = carregar_voos()
    codigo = request.form['codigo'].upper()
    if codigo in voos:
        flash('Código já existe.', 'danger')
    else:
        voos[codigo] = {
            "Origem": request.form['origem'], 
            "Destino": request.form['destino'],
            "Milhas": int(request.form['milhas']), 
            "Preco": float(request.form['preco']),
            "Aeronave": request.form['aeronave'], 
            "Assentos": int(request.form['assentos']),
            "Data": request.form['data']  # Novo campo Data
        }
        salvar_todos_voos(voos)
        atualizar_grafo_voos() # Atualiza o grafo global de voos
        flash('Voo adicionado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/voo/edit/<string:codigo>')
def edit_voo_page(codigo):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    voos = carregar_voos()
    return render_template('admin/edit_voo.html', codigo=codigo, voo=voos.get(codigo))

@admin_bp.route('/voo/update/<string:codigo>', methods=['POST'])
def update_voo(codigo):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    voos = carregar_voos()
    if codigo in voos:
        voos[codigo].update({
            "Origem": request.form['origem'], 
            "Destino": request.form['destino'],
            "Milhas": int(request.form['milhas']), 
            "Preco": float(request.form['preco']),
            "Aeronave": request.form['aeronave'], 
            "Assentos": int(request.form['assentos']),
            "Data": request.form['data']  # Atualiza Data
        })
        salvar_todos_voos(voos)
        atualizar_grafo_voos() # Atualiza o grafo global de voos
        flash('Voo atualizado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/voo/delete/<string:codigo>')
def delete_voo(codigo):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    voos = carregar_voos()
    if voos.pop(codigo, None):
        salvar_todos_voos(voos)
        atualizar_grafo_voos() # Atualiza o grafo global de voos
        flash('Voo excluído.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    lista = []
    if request.method == 'POST':
        busca = request.form.get('busca')
        tipo = request.form.get('tipo')
        if tipo == 'cpf':
            lista = buscar_cliente_por_cpf(busca) or []
        elif tipo == 'nome':
            lista = buscar_cliente_por_nome(busca.lower()) or []
        elif tipo == 'inicial':
            lista = buscar_cliente_por_inicial(busca.lower())
    else:
        sort_by = request.args.get('sort_by', 'nome')
        if sort_by == 'cpf':
            lista = get_todos_clientes_por_cpf()
        else:
            lista = get_todos_clientes()

    current_sort = request.args.get('sort_by', 'nome')
    return render_template('admin/clientes.html', clientes=lista, current_sort=current_sort)

@admin_bp.route('/cliente/delete/<string:cpf>')
def delete_cliente(cpf):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    if excluir_cliente_por_cpf(cpf):
        flash(f'Cliente {cpf} removido.', 'success')
    else:
        flash('Erro ao remover.', 'danger')
    return redirect(url_for('admin.clientes'))