from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from flask_wtf.file import FileField, FileAllowed

class EmployerProfileForm(FlaskForm):
    company_name = StringField('Название компании', validators=[DataRequired(), Length(max=100)])
    company_description = TextAreaField('Описание компании', validators=[Optional(), Length(max=1000)])
    industry = SelectField('Отрасль', choices=[
        ('', 'Выберите отрасль'),
        ('IT', 'Информационные технологии'),
        ('finance', 'Финансы'),
        ('healthcare', 'Здравоохранение'),
        ('education', 'Образование'),
        ('marketing', 'Маркетинг'),
        ('management', 'Менеджмент'),
        ('design', 'Дизайн'),
        ('other', 'Другое')
    ])
    website = StringField('Вебсайт', validators=[Optional(), Length(max=200)])
    team_size = SelectField('Размер команды', choices=[
        ('', 'Не указано'),
        ('1-10', '1-10 человек'),
        ('11-50', '11-50 человек'),
        ('51-200', '51-200 человек'),
        ('201+', 'Более 200 человек')
    ])
    preferred_mbti = SelectField('Предпочтительные MBTI-типы', choices=[
        ('', 'Не важно'),
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')
    ])
    submit = SubmitField('Сохранить настройки')

class VacancyForm(FlaskForm):
    title = StringField('Название должности', validators=[DataRequired(), Length(max=100)])
    company = StringField('Название компании', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Описание вакансии', validators=[DataRequired()])
    requirements = TextAreaField('Требования', validators=[DataRequired()])
    location = StringField('Местоположение', validators=[DataRequired()])
    salary_range = StringField('Зарплатная вилка', validators=[DataRequired()])
    industry = SelectField('Отрасль', choices=[
        ('', 'Выберите отрасль'),
        ('IT', 'Информационные технологии'),
        ('finance', 'Финансы'),
        ('healthcare', 'Здравоохранение'),
        ('education', 'Образование'),
        ('marketing', 'Маркетинг'),
        ('management', 'Менеджмент'),
        ('design', 'Дизайн'),
        ('other', 'Другое')
    ], validators=[DataRequired()])
    required_mbti = SelectField('Предпочтительные MBTI-типы', choices=[
        ('', 'Не важно'),
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')
    ])
    stress = StringField('Уровень стрессоустойчивости', validators=[Length(max=50)])
    submit = SubmitField('Создать вакансию')

class AvatarForm(FlaskForm):
    avatar = FileField('Логотип компании', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения (jpg, jpeg, png)')
    ])
    submit = SubmitField('Загрузить логотип')