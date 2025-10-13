from flask import Flask, render_template, request

app = Flask(__name__)

#criar a 1 pagina do site
# route -> qual e o caminho depois do seu dominio  ex: ..../usuarios
#funcao -> o que quer exibir naquela pagina
#template

@app.route('/home/')
def homepage():
    return render_template("homepage.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        return render_template('login.html')
    else:
        return show_the_login_form()




# colocar o site no ar
if __name__ == "__main__":
    app.run(debug=True)

