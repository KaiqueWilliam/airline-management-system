import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template

app = Flask(__name__, template_folder='app/templates')
# from app.routes.admin_routes import admin_bp
# from app.routes.voo_routes import voo_bp

# app.secret_key = "segredo123"

# app.register_blueprint(admin_bp)
# app.register_blueprint(voo_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
