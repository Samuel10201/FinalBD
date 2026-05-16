import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from dotenv import load_dotenv
from routes.auth import auth_bp
from routes.config_academica import config_academica_bp
from routes.config_operativa import config_operativa_bp
from routes.matricula import matricula_bp
from routes.pagos import pagos_bp
from routes.cuenta_corriente import cuenta_corriente_bp
from routes.reportes import reportes_bp

def create_app():
    load_dotenv()
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = os.environ['SECRET_KEY']

    app.register_blueprint(auth_bp)
    app.register_blueprint(config_academica_bp)
    app.register_blueprint(config_operativa_bp)
    app.register_blueprint(matricula_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(cuenta_corriente_bp)
    app.register_blueprint(reportes_bp)

    @app.after_request
    def no_cache(response):
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response

    return app


# Crear la instancia de la app para Vercel
app = create_app()

if __name__ == '__main__':
      app.run(debug=True)
