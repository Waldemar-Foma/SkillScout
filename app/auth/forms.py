from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class UnifiedRegistrationForm(FlaskForm):
    role = SelectField('Выберите роль', choices=[
        ('candidate', 'Кандидат'),
        ('employer', 'Работодатель')
    ], validators=[DataRequired(message='Пожалуйста, выберите роль')])

    # Общие поля
    email = StringField('Email', validators=[
        DataRequired(message='Введите email'),
        Email(message='Введите корректный email')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=8, message='Пароль должен быть не менее 8 символов')
    ])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(message='Повторите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])

    # Поля кандидата
    fullname = StringField('ФИО')
    field = SelectField('Сфера деятельности', choices=[
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
        existing_user = User.query.filter_by(email=email.data).first()
        if existing_user:
            raise ValidationError('Пользователь с таким email уже существует.')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Отправить инструкции')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Аккаунт с таким email не найден.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Изменить пароль')
