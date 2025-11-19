from flask import render_template, request, redirect, url_for, flash, Blueprint, current_app, Response
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.forms import LoginForm, UnifiedRegistrationForm, ForgotPasswordForm
from app.models.user import User
from app.forms import QuestionnaireForm
from flask_mail import Message
from app import mail
import re
from io import BytesIO

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')
employer_bp = Blueprint('employer', __name__, url_prefix='/employer')

@main_bp.route('/avatar/<int:user_id>')
def get_avatar(user_id):
    user = User.query.get_or_404(user_id)
    return Response(user.avatar, mimetype='image/jpeg')  # или 'image/png'

@main_bp.route('/')
def index():
    return render_template('main/index.html')

@main_bp.route('/about')
def about():
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    return render_template('main/contact.html')

@main_bp.route('/questionnaire', methods=['GET', 'POST'])
@login_required
def questionnaire():
    form = QuestionnaireForm()

    if form.validate_on_submit():
        flash('Анкета успешно сохранена!', 'success')
        return redirect(url_for('main.index'))

    return render_template('main/questionnaire.html', form=form)

# Аутентификация
@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
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
            return redirect(url_for(f'{user.role}.dashboard'))
        flash('Неверный email или пароль', 'danger')
    return render_template('auth/login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main_bp.route('/send_question', methods=['POST'])
def send_question():
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')  # Это будет email/telegram отправителя
        question = request.form.get('question')
        
        # Жестко задаем получателя (ваш служебный email)
        recipient_email = "eayrapetyan2009@gmail.com"  # Меняйте на свой!
        
        try:
            msg = Message(
                subject=f"Вопрос от {name}",
                sender=contact,  # Отправитель = email/telegram пользователя
                recipients=[recipient_email],  # Получатель = ваш email
                reply_to=contact  # Чтобы ответить пользователю
            )
            msg.body = f"""
            Имя: {name}
            Контакт: {contact}
            Вопрос:
            {question}
            """
            mail.send(msg)
            flash('Сообщение отправлено!', 'success')
        except Exception as e:
            flash('Ошибка отправки. Попробуйте позже.', 'danger')
        
        return redirect(url_for('main.index'))
    
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = UnifiedRegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash('Email уже зарегистрирован.', 'danger')
            return redirect(url_for('auth.register'))

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


@main_bp.route('/register/candidate', methods=['GET', 'POST'])
def register_candidate():
    form = UnifiedRegistrationForm()
    
    if form.validate_on_submit():
        password = form.password.data 
        password2 = form.password2.data 
        if re.search(r'\d', password) and re.search(r'[A-ZА-Я]', password) and re.search(r'[!@#$%^&*(),.?":{}|<>]', password) and password == password2:
            try:
                user = User(
                    email=form.email.data,
                    password_hash=generate_password_hash(form.password.data),
                    role='candidate',
                    fullname=form.fullname.data,
                    field=form.field.data,  # Теперь поле точно будет валидным
                    experience=form.experience.data or '',  # Защита от None
                    skills=form.skills.data or ''
                )
                db.session.add(user)
                db.session.commit()
                flash('Регистрация успешна!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
        else:
            return render_template('auth/register_candidate.html', form=form)

    return render_template('auth/register_candidate.html', form=form)

@main_bp.route('/register/employer', methods=['GET', 'POST'])
def register_employer():
    form = UnifiedRegistrationForm()

    if form.validate_on_submit():
        password = form.password.data 
        password2 = form.password2.data 
        if re.search(r'\d', password) and re.search(r'[A-ZА-Я]', password) and re.search(r'[!@#$%^&*(),.?":{}|<>]', password) and password == password2:
            try:
                user = User(
                    email=form.email.data,
                    password_hash=generate_password_hash(form.password.data),
                    role='employer',
                    company_name=form.company_name.data
                )
                db.session.add(user)
                db.session.commit()
                flash('Регистрация успешна!', 'success')
                return redirect(url_for('auth.login'))
            except Exception as e:
                db.session.rollback()
        else:
            return render_template('auth/register_employer.html', form=form)

    return render_template('auth/register_employer.html', form=form)

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

@main_bp.route('/politica')
def politica():
    return render_template('main/politica.html')

@main_bp.route('/tou')
def tou():
    return render_template('main/tou.html')
