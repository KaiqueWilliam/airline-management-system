from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session
)
from ..structures import (
    btree_cpf, btree_nome, carregar_clientes, 
    carregar_voos, salvar_todos_voos 
)

admin_bp = Blueprint(
    'admin', 
    __name__, 
    url_prefix='/admin',
    template_folder='templates' 
)

admin_users = {
    "admin": "1234"
}

# Carrega voos iniciais
voos = carregar_voos()

@admin_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in admin_users and admin_users[username] == password:
            session['logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Usuário ou senha inválidos.', 'danger')
 
    return render_template('admin/admin_login.html')

@admin_bp.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('admin.login'))
    
    # Recarrega para garantir dados atuais
    global voos
    voos = carregar_voos()
    
    return render_template('admin/admin_dashboard.html', voos=voos)

@admin_bp.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@admin_bp.route('/voo/add', methods=['POST'])
def add_voo():
    if not session.get('logged_in'):
        return redirect(url_for('admin.login'))
    try:
        global voos
        voos = carregar_voos()
        codigo = request.form['codigo'].upper()
        
        if codigo in voos:
            flash(f"Erro: O código de voo '{codigo}' já existe.", 'danger')
            return redirect(url_for('admin.dashboard'))
        
        voos[codigo] = {
            "Origem": request.form['origem'], "Destino": request.form['destino'],
            "Milhas": int(request.form['milhas']), "Preco": float(request.form['preco']),
            "Aeronave": request.form['aeronave'], "Assentos": int(request.form['assentos'])
        }
        salvar_todos_voos(voos)
        flash(f"Voo {codigo} cadastrado com sucesso!", 'success')
    except Exception as e:
        flash(f"Erro ao cadastrar voo: {e}", 'danger')

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/voo/edit/<string:codigo>', methods=['GET'])
def edit_voo_page(codigo):
    if not session.get('logged_in'):
        return redirect(url_for('admin.login'))
    
    global voos
    voos = carregar_voos()
    voo = voos.get(codigo)
    
    if not voo:
        flash(f"Voo {codigo} não encontrado.", 'danger')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_voo.html', codigo=codigo, voo=voo)

@admin_bp.route('/voo/update/<string:codigo>', methods=['POST'])
def update_voo(codigo):
    if not session.get('logged_in'):
        return redirect(url_for('admin.login'))
    
    global voos
    voos = carregar_voos()
    
    if codigo not in voos:
        flash(f"Voo {codigo} não encontrado.", 'danger')
        return redirect(url_for('admin.dashboard'))
    try:
        voos[codigo] = {
            "Origem": request.form['origem'], "Destino": request.form['destino'],
            "Milhas": int(request.form['milhas']), "Preco": float(request.form['preco']),
            "Aeronave": request.form['aeronave'], "Assentos": int(request.form['assentos'])
        }
        salvar_todos_voos(voos)
        flash(f"Voo {codigo} atualizado com sucesso!", 'success')
    except Exception as e:
        flash(f"Erro ao atualizar voo: {e}", 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/voo/delete/<string:codigo>')
def delete_voo(codigo):
    if not session.get('logged_in'):
        return redirect(url_for('admin.login'))
    
    global voos
    voos = carregar_voos()
    
    if voos.pop(codigo, None):
        salvar_todos_voos(voos)
        flash(f"Voo {codigo} excluído com sucesso!", 'success')
    else:
        flash(f"Erro: Voo {codigo} não encontrado.", 'danger')
    
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/clientes', methods=['GET', 'POST'])
def clientes():
    if not session.get('logged_in'): return redirect(url_for('admin.login'))
    
    lista = []
    if request.method == 'POST':
        busca = request.form.get('busca')
        tipo = request.form.get('tipo')
        
        if tipo == 'cpf':
            res = btree_cpf.search(busca)
            if res: lista = [res]
        elif tipo == 'nome':
            res = btree_nome.search(busca.lower())
            if res: lista = [res]
        elif tipo == 'inicial':
            todos = btree_nome.inorder_traversal()
            lista = [c for c in todos if c['nome'].lower().startswith(busca.lower())]
    else:
        # Carregar todos (em ordem de nome)
        lista = btree_nome.inorder_traversal()

    return render_template('admin/clientes.html', clientes=lista)