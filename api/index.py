import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from flask import Flask
from dotenv import load_dotenv
from routes.auth import auth_bp

def create_app():
    #Crea la app Flask, carga configuracion, registra blueprints y retorna la app.
    
    #Carga las variables de ambiente
    load_dotenv()
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.secret_key = os.environ['SECRET_KEY']
    
    app.register_blueprint(auth_bp)

    return app


app = create_app()

if __name__ == '__main__':
      app.run(debug=True)
