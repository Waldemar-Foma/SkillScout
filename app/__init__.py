from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    db.init_app(app)
    login_manager.init_app(app)
    
    # Регистрация Blueprint'ов
    from .auth.routes import auth_bp
    from .candidate.routes import candidate_bp
    from .employer.routes import employer_bp
    from .main.routes import main_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(candidate_bp, url_prefix='/candidate')
    app.register_blueprint(employer_bp, url_prefix='/employer')
    app.register_blueprint(main_bp)
    
    return app