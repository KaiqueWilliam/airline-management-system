from flask import Flask, render_template

def create_app():
    
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'trabalho-ed2-uneb'

    
    from .routes.admin_routes import admin_bp
    app.register_blueprint(admin_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    return app