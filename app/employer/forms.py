from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField
from wtforms.validators import DataRequired, Length

class EmployerProfileForm(FlaskForm):
    company_name = StringField('Название компании', validators=[DataRequired(), Length(max=100)])
    company_description = TextAreaField('Описание компании')
    industry = SelectField('Отрасль', choices=[
        ('IT', 'Информационные технологии'),
        ('finance', 'Финансы'),
        ('healthcare', 'Здравоохранение'),
        ('education', 'Образование'),
        ('other', 'Другое')
    ])
    website = StringField('Вебсайт')
    team_size = SelectField('Размер команды', choices=[
        ('1-10', '1-10 человек'),
        ('11-50', '11-50 человек'),
        ('51-200', '51-200 человек'),
        ('201+', 'Более 200 человек')
    ])

class VacancyForm(FlaskForm):
    title = StringField('Должность', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Описание вакансии', validators=[DataRequired()])
    requirements = TextAreaField('Требования', validators=[DataRequired()])
    location = StringField('Локация')
    salary_range = StringField('Зарплатная вилка')
    is_remote = BooleanField('Удалённая работа')
    required_mbti = StringField('Предпочтительные MBTI-типы')