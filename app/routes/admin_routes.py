from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


admins = {
    "admin": generate_password_hash("1234")  
}
 
if "admin" not in admins:
    admins["admin"] = generate_password_hash("1234")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form.get('usuario').strip()
        senha = request.form.get('senha')

        senha_hash = admins.get(usuario)
        if senha_hash and check_password_hash(senha_hash, senha):
            session['admin'] = usuario
            flash("Login administrativo efetuado.", "success")
            return redirect(url_for('voos.listar_voos'))
        else:
            flash("Usuário ou senha incorretos.", "danger")
            return redirect(url_for('admin.login'))

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin', None)
    flash("Logout administrativo efetuado.", "info")
    return redirect(url_for('index'))
