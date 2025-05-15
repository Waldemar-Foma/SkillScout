from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from app.extensions import db
from app.forms import LoginForm, RegistrationForm, ForgotPasswordForm, ResetPasswordForm
from app.models.user import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])  # Добавлен недостающий маршрут
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)

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
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    return render_template('main/plan.html')

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Недействительная или просроченная ссылка', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль был изменён', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)