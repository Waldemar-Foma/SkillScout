from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Инициализация расширений
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    
    # Инициализация расширений
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Регистрация blueprints
    from app.main.routes import main_bp
    app.register_blueprint(main_bp)
    
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.candidate.routes import candidate_bp
    app.register_blueprint(candidate_bp, url_prefix='/candidate')
    
    from app.employer.routes import employer_bp
    app.register_blueprint(employer_bp, url_prefix='/employer')
    
    return app