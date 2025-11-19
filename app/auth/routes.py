from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from app.extensions import db, mail
from app.forms import LoginForm, UnifiedRegistrationForm, ForgotPasswordForm, ResetPasswordForm, ChangePasswordForm, ChangeMailForm
from app.models.user import User
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = UnifiedRegistrationForm()

    if form.validate_on_submit():
        print("Form validated successfully")
        user = User(
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data),
            role=form.role.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Регистрация успешна!', 'success')
        return redirect(url_for('auth.login'))
    else:
        print("Form errors:", form.errors)


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
            return redirect(url_for(f'{user.role}.dashboard'))
        flash('Неверный email или пароль', 'danger')
    return render_template('auth/login.html', title='Sign In', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            try:
                token = user.generate_reset_token()  # Метод экземпляра
                reset_url = url_for('auth.reset_password', token=token, _external=True)
                
                msg = Message(
                    "Сброс пароля SkillScout",
                    sender=current_app.config['MAIL_DEFAULT_SENDER'],
                    recipients=[user.email]
                )
                msg.body = f"Перейдите по ссылке для сброса пароля:\n{reset_url}"
                
                mail.send(msg)
                flash("Инструкции отправлены на ваш email.", "success")
            except Exception as e:
                current_app.logger.error(f"SMTP Error: {e}")
                flash("Ошибка отправки. Попробуйте позже.", "danger")
            return redirect(url_for('auth.login'))
    
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    # Проверяем токен, но не перенаправляем сразу при ошибке
    email = User.verify_reset_token(token)
    if not email:
        flash('Недействительная или просроченная ссылка', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('Пользователь не найден', 'danger')
        return redirect(url_for('auth.forgot_password'))
    
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            if form.password.data == form.password2.data and re.search(r'[!@#$%^&*(),.?":{}|<>]', form.password.data) and re.search(r'[A-ZА-Я]', form.password.data) and re.search(r'\d', form.password.data):
                user.set_password(form.password.data)
                db.session.commit()
                flash('Ваш пароль был успешно изменен. Теперь вы можете войти.', 'success')
                return redirect(url_for('auth.login'))
            else:
                return render_template('auth/reset_password.html', title='Сброс пароля', form=form, token=token)
        except Exception as e:
            db.session.rollback()
            flash('Произошла ошибка при изменении пароля. Пожалуйста, попробуйте снова.', 'danger')
    
    # Если форма не прошла валидацию, остаемся на той же странице
    # Ошибки уже будут показаны через валидаторы формы
    return render_template('auth/reset_password.html', title='Сброс пароля', form=form, token=token)

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        try:
            # Проверяем старый пароль
            if not current_user.check_password(form.old_password.data):
                flash('Неверный текущий пароль', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
            
            # Проверяем новый пароль на соответствие требованиям
            new_password = form.password.data
            
            # Проверка совпадения паролей
            if new_password != form.password2.data:
                flash('Новые пароли не совпадают', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
            
            # Проверка сложности пароля
            if len(new_password) < 8:
                flash('Пароль должен содержать минимум 8 символов', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
                
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', new_password):
                flash('Пароль должен содержать хотя бы один специальный символ', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
                
            if not re.search(r'[A-ZА-Я]', new_password):
                flash('Пароль должен содержать хотя бы одну заглавную букву', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
                
            if not re.search(r'\d', new_password):
                flash('Пароль должен содержать хотя бы одну цифру', 'danger')
                return render_template('auth/change_password.html', title='Смена пароля', form=form)
            
            # Устанавливаем новый пароль
            current_user.set_password(new_password)
            db.session.commit()
            flash('Ваш пароль был успешно изменен', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Ошибка при изменении пароля: {str(e)}')
            flash(f'Произошла ошибка: {str(e)}', 'danger')
    
    return render_template('auth/change_password.html', title='Смена пароля', form=form)

@auth_bp.route('/change-mail', methods=['GET', 'POST'])
@login_required
def change_mail():
    form = ChangeMailForm()
    
    if form.validate_on_submit():
        try:
            new_mail = form.mail.data
            
            current_user.set_email(new_mail)
            db.session.commit()
            flash('Ваша почта была успешно изменена', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Эта почта уже занята')
            flash('Эта почта уже занята', 'danger')
    
    return render_template('auth/change_mail.html', title='Смена почты', form=form)