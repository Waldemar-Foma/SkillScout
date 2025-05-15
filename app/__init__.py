import os
from flask import Flask, render_template
from app.extensions import db, login_manager, mail, migrate, csrf

def create_app(config_class='config.Config'):
    app = Flask(__name__, static_folder='static')
    app.config.from_object(config_class)

    # Инициализация расширений
    csrf.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)
    mail.init_app(app)

    app.static_url_path = '/static'
    app.static_folder = os.path.join(app.root_path, 'static')

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    login_manager.session_protection = "strong"

    # Импорт модели
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Регистрация blueprints
    from app.main.routes import main_bp
    from app.auth.routes import auth_bp
    from app.candidate.routes import candidate_bp
    from app.employer.routes import employer_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(candidate_bp)
    app.register_blueprint(employer_bp)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        return render_template('error/500.html'), 500

    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully")
            from sqlalchemy import inspect
            insp = inspect(db.engine)
            print("Tables in database:", insp.get_table_names())
        except Exception as e:
            print(f"❌ Database error: {str(e)}")
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1]
            print(f"Database path: {db_path}")
            print(f"Path exists: {os.path.exists(db_path)}")
            print(f"Write access: {os.access(os.path.dirname(db_path), os.W_OK)}")

    return app
