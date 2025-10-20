import os
import sys

# garante que 'app' seja encontrado caso rode de níveis diferentes
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from flask import Flask, render_template

# cria app apontando para templates e static dentro da pasta 'app'
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "app", "templates"),
    static_folder=os.path.join(BASE_DIR, "app", "static")
)
app.secret_key = "segredo123"

# registrar blueprints
from app.routes.admin_routes import admin_bp
from app.routes.voo_routes import voo_bp
from app.routes.passenger_routes import passenger_bp  # novo

app.register_blueprint(admin_bp)
app.register_blueprint(voo_bp)
app.register_blueprint(passenger_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
