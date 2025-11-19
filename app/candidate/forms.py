from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, SelectField, TextAreaField, Label
from wtforms.validators import DataRequired, Length, NumberRange
from flask_wtf.file import FileField, FileAllowed

class CandidateProfileForm(FlaskForm):
    field = SelectField('Сфера деятельности', choices=[
        ('', ''),  # Добавляем пустой вариант
        ('IT', 'IT'),
        ('Маркетинг', 'Маркетинг'),
        ('Менеджмент', 'Менеджмент'),
        ('Дизайн', 'Дизайн'),
        ('Другое', 'Другое')
    ])
    profession = StringField('Профессия', validators=[DataRequired(), Length(max=100)])
    experience = IntegerField('Опыт работы (лет)', validators=[NumberRange(min=0)])
    skills = TextAreaField('Ключевые навыки')
    mbti_type = SelectField('Психологический тип (MBTI)', choices=[
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')
    ])
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения (jpg, jpeg, png)')
    ])
    video_resume = FileField('Видеовизитка', validators=[
        FileAllowed(['mp4', 'mov', 'avi'], 'Только видеофайлы (mp4, mov, avi)')
    ])
    submit = SubmitField('Подтвердить')

class VacancyForm(FlaskForm):
    title = StringField('Название должности', render_kw={'readonly': True})
    company = StringField('Название компании', render_kw={'readonly': True})
    description = TextAreaField('Описание вакансии', render_kw={'readonly': True})
    requirements = TextAreaField('Требования', render_kw={'readonly': True})
    location = StringField('Местоположение', render_kw={'readonly': True})
    salary_range = StringField('Зарплатная вилка', render_kw={'readonly': True})
    industry = StringField('Отрасль', render_kw={'readonly': True})
    required_mbti = StringField('Предпочтительные MBTI-типы', render_kw={'readonly': True})
    stress = StringField('Уровень', render_kw={'readonly': True})

    tryit = SubmitField('Откликнуться')

class AvatarForm(FlaskForm):
    avatar = FileField('Аватар', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Только изображения (jpg, jpeg, png)')
    ])
    submit = SubmitField('Загрузить аватар')

class VideoResumeForm(FlaskForm):
    video_resume = FileField('Видеовизитка', validators=[
        FileAllowed(['mp4', 'mov', 'avi'], 'Только видеофайлы (mp4, mov, avi)')
    ])
    submit = SubmitField('Загрузить видео')