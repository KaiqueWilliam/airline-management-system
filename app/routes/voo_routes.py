from flask import Blueprint, render_template, request, redirect, url_for, flash

voo_bp = Blueprint('voos', __name__, url_prefix='/voos')

# DICIONÁRIO OBRIGATÓRIO DE VOOS (exigido pelo trabalho)
voos = {
    "LA1001": {"origem": "São Paulo", "destino": "Rio de Janeiro", "horario": "08:30", "preco": 450},
    "LA1002": {"origem": "Rio de Janeiro", "destino": "Brasília", "horario": "10:45", "preco": 520},
    "LA1003": {"origem": "Curitiba", "destino": "Salvador", "horario": "13:15", "preco": 670}
}

@voo_bp.route('/listar')
def listar_voos():
    return render_template('voos/list.html', voos=voos)


@voo_bp.route('/add', methods=['GET', 'POST'])
def add_voo():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        origem = request.form.get('origem')
        destino = request.form.get('destino')
        horario = request.form.get('horario')
        preco = float(request.form.get('preco'))

        if codigo in voos:
            flash("Já existe um voo com esse código.", "danger")
        else:
            voos[codigo] = {"origem": origem, "destino": destino, "horario": horario, "preco": preco}
            flash("Voo adicionado com sucesso!", "success")

        return redirect(url_for('voos.listar_voos'))

    return render_template('voos/add_flights.html')
