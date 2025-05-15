from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm  # Добавлен импорт
from app.models.user import User

# Инициализация Blueprints
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')
employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

# Главные маршруты
@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

# Аутентификация
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])  # Исправлено с bp на auth_bp
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        flash('Инструкции по сбросу пароля отправлены на ваш email', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for(f'{user.role}.dashboard'))
        flash('Неверный email или пароль', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            email=form.email.data,
            password_hash=hashed_password,
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)

# Кандидаты
@candidate_bp.route('/dashboard')
@login_required
def candidate_dashboard():
    if current_user.role != 'candidate':
        return redirect(url_for('main.index'))
    return render_template('candidate/dashboard.html')

# Работодатели
@employer_bp.route('/dashboard')
@login_required
def employer_dashboard():
    if current_user.role != 'employer':
        return redirect(url_for('main.index'))
    return render_template('employer/dashboard.html')

# Ошибки
@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    current_app.logger.error(f'Server error: {e}')
    return render_template('error/500.html'), 500
