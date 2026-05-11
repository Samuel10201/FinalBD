import os
from flask import Flask
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


def create_app():
    """Crea la app Flask, carga configuracion, registra blueprints y retorna la app.
    
    Esta es la función principal que TODOS los blueprints deben atravesar.
    Otros desarrolladores pueden agregar sus blueprints aquí.
    """
    app = Flask(__name__)
    
    # ===================== CONFIGURACIÓN =====================
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    app.config['SESSION_TYPE'] = 'filesystem'
    
    
    # ===================== INICIALIZAR EXTENSIONES =====================
    # TODO: Agregar otras extensiones (session, etc) aquí
    
    
    # ===================== REGISTRAR BLUEPRINTS =====================
    # Importar blueprints
    from routes.auth import auth_bp
    from routes.matricula import matricula_bp
    # Importar otros blueprints cuando estén listos:
    # from routes.config_academica import config_academica_bp
    # from routes.config_operativa import config_operativa_bp
    # from routes.pagos import pagos_bp
    # from routes.cuenta_corriente import cuenta_corriente_bp
    # from routes.reportes import reportes_bp
    
    # Registrar blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(matricula_bp)
    # app.register_blueprint(config_academica_bp)
    # app.register_blueprint(config_operativa_bp)
    # app.register_blueprint(pagos_bp)
    # app.register_blueprint(cuenta_corriente_bp)
    # app.register_blueprint(reportes_bp)
    
    
    # ===================== RUTAS ESPECIALES =====================
    @app.route('/')
    def index():
        """Página de inicio. Redirige según el rol del usuario."""
        # TODO: Implementar dashboard con redirección por rol
        return "Sistema de Cuenta Corriente - Página de inicio (TODO)"
    
    
    return app


# Crear la instancia de la app para Vercel
app = create_app()
