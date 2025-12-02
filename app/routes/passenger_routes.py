from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..structures import (
    Graph, salvar_cliente, salvar_compra, gerar_codigo_reserva,
    carregar_voos, salvar_todos_voos
)

passenger_bp = Blueprint('passenger', __name__, template_folder='templates')

@passenger_bp.route('/search', methods=['GET', 'POST'])
def search_flights():
    voos = carregar_voos()

    if request.method == 'POST':
        origem = request.form['origem']
        destino = request.form['destino']
        
        # 1. Montar Grafo
        graph = Graph()
        for codigo, dados in voos.items():
            graph.add_flight(dados['Origem'], dados['Destino'], codigo, dados['Preco'])

        # 2. Busca Direta
        diretos = []
        for codigo, dados in voos.items():
            if dados['Origem'].lower() == origem.lower() and dados['Destino'].lower() == destino.lower():
                diretos.append({'codigos': [codigo], 'dados': [dados], 'total': dados['Preco']})

        # 3. Busca Conexão (Grafo)
        caminho, custo = graph.find_best_route(origem, destino)
        rota_conexao = None
        
        if caminho and (not diretos or caminho != diretos[0]['codigos']):
            dados_voos = [voos[c] for c in caminho]
            rota_conexao = {
                'codigos': caminho,
                'dados': dados_voos,
                'total': custo
            }

        return render_template('passenger/results.html', diretos=diretos, conexao=rota_conexao, origem=origem, destino=destino)

    cidades = set()
    for v in voos.values():
        cidades.add(v['Origem'])
        cidades.add(v['Destino'])
        
    return render_template('passenger/search.html', cidades=cidades)

@passenger_bp.route('/buy', methods=['POST'])
def buy_ticket():
    codigos_str = request.form['flight_codes']
    total = request.form['total_price']
    return render_template('passenger/buy.html', codigos=codigos_str.split(','), total=total)

@passenger_bp.route('/confirm', methods=['POST'])
def confirm_purchase():
    try:
        voos = carregar_voos()

        nome = request.form['nome']
        cpf = request.form['cpf']
        data_viagem = request.form['data']
        codigos = eval(request.form['codigos'])
        total = float(request.form['total'])

        milhas = 0
        for c in codigos:
            if voos[c]['Assentos'] <= 0:
                flash(f'Voo {c} lotado.', 'danger')
                return redirect(url_for('passenger.search_flights'))
            milhas += voos[c]['Milhas']

        for c in codigos:
            voos[c]['Assentos'] -= 1
        
        salvar_todos_voos(voos)

        reserva = gerar_codigo_reserva()

        cliente = {
            'cpf': cpf, 'nome': nome, 'reserva': reserva,
            'data': data_viagem, 'milhas': milhas
        }
        salvar_cliente(cliente)

        compra = {
            'reserva': reserva, 'voos': codigos, 'valor': total
        }
        salvar_compra(compra)

        flash(f'Compra Confirmada! Reserva: {reserva}', 'success')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Erro: {e}', 'danger')
        return redirect(url_for('passenger.search_flights'))