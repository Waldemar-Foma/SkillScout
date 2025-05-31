from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, NumberRange

class CandidateProfileForm(FlaskForm):
    profession = StringField('Профессия', validators=[DataRequired(), Length(max=100)])
    experience = IntegerField('Опыт работы (лет)', validators=[NumberRange(min=0)])
    skills = TextAreaField('Ключевые навыки')
    mbti_type = SelectField('Психологический тип (MBTI)', choices=[
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP')
    ])
    video_resume = FileField('Видеовизитка')