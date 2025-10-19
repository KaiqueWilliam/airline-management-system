from flask import Blueprint, render_template, request, redirect, url_for, session, flash

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

users = {
    "admin": "1234",
    "funcionario": "senha123"
}

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userAdmin = request.form.get('userAdmin')
        passwordAdmin = request.form.get('passwordAdmin')

        if userAdmin in users and users[userAdmin] == passwordAdmin:
            session['userAdmin'] = userAdmin
            flash("Login efetuado com sucesso")
            return redirect(url_for('voos.list_flights'))
        else: 
            flash("usuário ou senha incorretos!","danger")
            return redirect(url_for('admin.login'))
        

    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logout efetuado com sucesso.","info")
    return redirect(url_for('index'))
