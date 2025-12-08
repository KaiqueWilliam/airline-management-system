from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from ..structures import (
    Graph, salvar_cliente, salvar_compra, gerar_codigo_reserva,
    carregar_voos, salvar_todos_voos, salvar_novo_usuario, buscar_usuario_por_email
)

passenger_bp = Blueprint('passenger', __name__, template_folder='templates')

@passenger_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        senha = request.form['senha']
        
        senha_hash = generate_password_hash(senha)
        novo_usuario = { 'nome': nome, 'email': email, 'cpf': cpf, 'senha': senha_hash }
        
        if salvar_novo_usuario(novo_usuario):
            flash('Cadastro realizado! Faça login.', 'success')
            return redirect(url_for('passenger.login'))
        else:
            flash('E-mail já cadastrado.', 'danger')
    return render_template('passenger/register.html')

@passenger_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = buscar_usuario_por_email(email)
        
        if usuario and check_password_hash(usuario['senha'], senha):
            session['user_id'] = usuario['email']
            session['user_name'] = usuario['nome']
            session['user_cpf'] = usuario['cpf']
            flash(f'Bem-vindo, {usuario["nome"]}!', 'success')
            return redirect(request.args.get('next') or url_for('passenger.search_flights'))
        else:
            flash('Credenciais inválidas.', 'danger')
    return render_template('passenger/login.html')

@passenger_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('passenger.login'))

@passenger_bp.route('/search', methods=['GET', 'POST'])
def search_flights():
    voos = carregar_voos()
    if request.method == 'POST':
        origem = request.form['origem']
        destino = request.form['destino']
        
        graph = Graph()
        for codigo, dados in voos.items():
            graph.add_flight(dados['Origem'], dados['Destino'], codigo, dados['Preco'])

        diretos = []
        for codigo, dados in voos.items():
            if dados['Origem'].lower() == origem.lower() and dados['Destino'].lower() == destino.lower():
                diretos.append({'codigos': [codigo], 'dados': [dados], 'total': dados['Preco']})

        caminho, custo = graph.find_best_route(origem, destino)
        rota_conexao = None
        if caminho and (not diretos or caminho != diretos[0]['codigos']):
            dados_voos = [voos[c] for c in caminho]
            rota_conexao = { 'codigos': caminho, 'dados': dados_voos, 'total': custo }

        return render_template('passenger/results.html', diretos=diretos, conexao=rota_conexao, origem=origem, destino=destino)

    cidades = set()
    for v in voos.values():
        cidades.add(v['Origem'])
        cidades.add(v['Destino'])
        
    return render_template('passenger/search.html', cidades=cidades, voos=voos)

@passenger_bp.route('/buy', methods=['POST'])
def buy_ticket():
    if 'user_id' not in session:
        flash('Faça login para comprar.', 'warning')
        return redirect(url_for('passenger.login', next=request.referrer))

    codigos_str = request.form['flight_codes']
    codigos_lista = codigos_str.split(',')
    total = request.form['total_price']
    
    # Busca a data do primeiro voo para exibir
    voos = carregar_voos()
    primeiro_voo = voos.get(codigos_lista[0])
    data_viagem = primeiro_voo['Data'] if primeiro_voo else "N/A"

    return render_template('passenger/buy.html', 
                           codigos=codigos_lista, 
                           total=total,
                           data_viagem=data_viagem, # Passa a data fixa
                           user_name=session.get('user_name'),
                           user_cpf=session.get('user_cpf'))

@passenger_bp.route('/confirm', methods=['POST'])
def confirm_purchase():
    if 'user_id' not in session: return redirect(url_for('passenger.login'))
    try:
        voos = carregar_voos()
        nome = session['user_name']
        cpf = session['user_cpf']
        codigos = eval(request.form['codigos'])
        total = float(request.form['total'])

        # AUTOMÁTICO: Pega a data do primeiro voo
        primeiro_voo = voos.get(codigos[0])
        data_viagem = primeiro_voo['Data'] if primeiro_voo else "N/A"

        milhas = 0
        for c in codigos:
            if voos[c]['Assentos'] <= 0:
                flash(f'Voo {c} lotado.', 'danger')
                return redirect(url_for('passenger.search_flights'))
            milhas += voos[c]['Milhas']

        for c in codigos: voos[c]['Assentos'] -= 1
        
        salvar_todos_voos(voos)
        reserva = gerar_codigo_reserva()

        cliente = { 'cpf': cpf, 'nome': nome, 'reserva': reserva, 'data': data_viagem, 'milhas': milhas }
        salvar_cliente(cliente)

        compra = { 'reserva': reserva, 'voos': codigos, 'valor': total, 'comprador': session['user_id'] }
        salvar_compra(compra)

        flash(f'Sucesso! Reserva: {reserva}', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
        return redirect(url_for('passenger.search_flights'))