from flask import flash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models.user import User
import re
from flask_wtf.file import FileField, FileRequired, FileAllowed
from config import Config

def validate_password_complexity(form, field):
    password = field.data
    
    if not re.search(r'\d', password):
        flash('Пароль должен содержать хотя бы одну цифру', 'danger')
    
    if not re.search(r'[A-ZА-Я]', password):
        flash('Пароль должен содержать хотя бы одну заглавную букву', 'danger')
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        flash('Пароль должен содержать хотя бы один специальный символ', 'danger')
    
class AvatarForm(FlaskForm):
    avatar = FileField('Аватар', validators=[
        FileAllowed(Config.ALLOWED_EXTENSIONS, 'Только изображения!')
    ])
    video_resume = FileField('Video Resume', validators=[
        FileAllowed(['mp4', 'mov', 'avi'], 'Video files only!')
    ])
    submit = SubmitField('Обновить')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(message='Введите email'), Email(message='Некорректный email')])
    password = PasswordField('Пароль', validators=[DataRequired(message='Введите пароль')])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

def passwords_match(form, field):
    if field.data != form.password.data:
        flash("Пароли не совпадают", 'danger')

class UnifiedRegistrationForm(FlaskForm):
    fullname = StringField('ФИО')  # Только для кандидата

    role = SelectField('Роль', choices=[
        ('candidate', 'Кандидат'),
        ('employer', 'Работодатель')
    ], validators=[DataRequired()])
    
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(max=120)
    ])
    
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=8),
        validate_password_complexity
    ])
    
    password2 = PasswordField('Подтверждение', validators=[
        DataRequired(),
        passwords_match  # Наш кастомный валидатор
    ])
    field = SelectField('Сфера деятельности', choices=[
        ('', ''),  # Добавляем пустой вариант
        ('IT', 'IT'),
        ('Маркетинг', 'Маркетинг'),
        ('Менеджмент', 'Менеджмент'),
        ('Дизайн', 'Дизайн'),
        ('Другое', 'Другое')
    ])
    experience = TextAreaField('Опыт работы')
    skills = StringField('Ключевые навыки')

    # Поля работодателя
    company_name = StringField('Название компании')
    industry = StringField('Отрасль')
    contact_person = StringField('Контактное лицо')
    description = TextAreaField('Описание компании')

    submit = SubmitField('Зарегистрироваться')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            flash('Пользователь с таким email уже существует.', 'danger')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Некорректный email')
    ])
    submit = SubmitField('Отправить инструкции')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            flash('Аккаунт с таким email не найден', 'danger')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[
        Length(min=8),
        validate_password_complexity,
        DataRequired(message='Введите пароль')])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        passwords_match  # Наш кастомный валидатор
    ])
    submit = SubmitField('Изменить пароль')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Текущий пароль', validators=[
        DataRequired(),    
        ])
    password = PasswordField('Новый пароль', validators=[
        DataRequired(),
        Length(min=8, message='Пароль должен быть не менее 8 символов'),
        validate_password_complexity
    ])
    password2 = PasswordField('Подтвердите новый пароль', validators=[
        DataRequired(message='Подтвердите пароль'),
        passwords_match
        ])
    submit = SubmitField('Изменить пароль')

class ChangeMailForm(FlaskForm):
    mail = StringField('Новая почта', validators=[
        DataRequired(),
        Email(),
        Length(max=120)
    ])
    submit = SubmitField('Изменить почту')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            flash('Пользователь с таким email уже существует.', 'danger')

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

class QuestionnaireForm(FlaskForm):
    fullname = StringField('ФИО', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    profession = StringField('Профессия', validators=[DataRequired()])
    experience = TextAreaField('Опыт работы', validators=[Optional()])
    skills = StringField('Навыки', validators=[Optional()])
    mbti_type = SelectField('MBTI тип', choices=[
        ('INTJ', 'INTJ'), ('INFJ', 'INFJ'), ('ENFP', 'ENFP'),
        ('ENTP', 'ENTP'), ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'),
        ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'), ('INFP', 'INFP'),
        ('ENFJ', 'ENFJ'), ('ISFP', 'ISFP'), ('ESFP', 'ESFP'),
        ('ISTP', 'ISTP'), ('ESTP', 'ESTP'), ('ENTJ', 'ENTJ')
    ], validators=[Optional()])
    submit = SubmitField('Сохранить')

