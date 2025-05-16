from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Sign In')

class UnifiedRegistrationForm(FlaskForm):
    role = SelectField('Выберите роль', choices=[
        ('candidate', 'Кандидат'),
        ('employer', 'Работодатель')
    ], validators=[DataRequired()])

    # Общие поля
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])

    # Поля кандидата
    fullname = StringField('ФИО')  # Только для кандидата
    field = SelectField('Сфера деятельности', choices=[
        ('IT', 'IT'), ('Маркетинг', 'Маркетинг'), ('Менеджмент', 'Менеджмент'), ('Дизайн', 'Дизайн'), ('Другое', 'Другое')
    ])
    experience = TextAreaField('Опыт работы')
    skills = StringField('Ключевые навыки')

    # Поля работодателя
    company_name = StringField('Название компании')
    industry = StringField('Отрасль')
    contact_person = StringField('Контактное лицо')
    description = TextAreaField('Описание компании')

    submit = SubmitField('Зарегистрироваться')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Отправить инструкции')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if not user:
            raise ValidationError('Аккаунт с таким email не найден')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password2 = PasswordField(
        'Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')