import os
import json
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

passenger_bp = Blueprint('passenger', __name__, url_prefix='/passenger')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
PASSENGERS_FILE = os.path.join(DATA_DIR, 'passengers.json')

os.makedirs(DATA_DIR, exist_ok=True)

def carregar_passageiros():
    if os.path.exists(PASSENGERS_FILE):
        with open(PASSENGERS_FILE, 'r', encoding='utf-8') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def salvar_passageiros(passageiros):
    with open(PASSENGERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(passageiros, f, indent=4, ensure_ascii=False)

passageiros = carregar_passageiros()


@passenger_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        identificador = request.form.get('cpf_email', '').strip().lower()
        senha = request.form.get('senha')

        if not nome or not identificador or not senha:
            flash("Preencha todos os campos.", "warning")
            return redirect(url_for('passenger.register'))

        if identificador in passageiros:
            flash("Usuário já cadastrado com esse CPF/E-mail.", "danger")
            return redirect(url_for('passenger.register'))

        senha_hash = generate_password_hash(senha)
        passageiros[identificador] = {
            "nome": nome,
            "cpf_email": identificador,
            "password_hash": senha_hash,
            "miles": 0
        }

        salvar_passageiros(passageiros)
        flash("Cadastro realizado com sucesso! Faça login.", "success")
        return redirect(url_for('passenger.login'))

    return render_template('passenger/register.html')


@passenger_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identificador = request.form.get('cpf_email', '').strip().lower()
        senha = request.form.get('senha')

        user = passageiros.get(identificador)
        if user and check_password_hash(user['password_hash'], senha):
            session['passenger'] = identificador
            flash(f"Bem-vindo(a), {user['nome']}!", "success")
            return redirect(url_for('passenger.dashboard'))
        else:
            flash("CPF/E-mail ou senha incorretos.", "danger")
            return redirect(url_for('passenger.login'))

    return render_template('passenger/login.html')


@passenger_bp.route('/dashboard')
def dashboard():
    """Painel principal do passageiro"""
    identificador = session.get('passenger')
    if not identificador:
        flash("Você precisa fazer login para acessar o painel.", "warning")
        return redirect(url_for('passenger.login'))

    user = passageiros.get(identificador)
    if not user:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for('passenger.login'))

    return render_template('passenger/dashboard.html', user=user)


@passenger_bp.route('/logout')
def logout():
    session.pop('passenger', None)
    flash("Logout efetuado.", "info")
    return redirect(url_for('index'))
