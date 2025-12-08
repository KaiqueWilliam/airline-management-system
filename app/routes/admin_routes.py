from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..structures import (
    carregar_voos, salvar_todos_voos, 
    excluir_cliente_por_cpf, get_todos_clientes, 
    buscar_cliente_por_cpf, buscar_cliente_por_nome, buscar_cliente_por_inicial
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')
admin_users = { "admin": "1234" }

@admin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in admin_users and admin_users[request.form['username']] == request.form['password']:
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
        flash('Voo atualizado.', 'success')
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/voo/delete/<string:codigo>')
def delete_voo(codigo):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    voos = carregar_voos()
    if voos.pop(codigo, None):
        salvar_todos_voos(voos)
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
            res = buscar_cliente_por_cpf(busca)
            if res: lista = [res]
        elif tipo == 'nome':
            res = buscar_cliente_por_nome(busca.lower())
            if res: lista = [res]
        elif tipo == 'inicial':
            lista = buscar_cliente_por_inicial(busca.lower())
    else:
        lista = get_todos_clientes()
    return render_template('admin/clientes.html', clientes=lista)

@admin_bp.route('/cliente/delete/<string:cpf>')
def delete_cliente(cpf):
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    if excluir_cliente_por_cpf(cpf):
        flash(f'Cliente {cpf} removido.', 'success')
    else:
        flash('Erro ao remover.', 'danger')
    return redirect(url_for('admin.clientes'))