from datetime import *
from app.extensions import db


class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_name = db.Column(db.String(100))
    company_description = db.Column(db.Text)
    company_logo = db.Column(db.String(255))
    industry = db.Column(db.String(50))
    website = db.Column(db.String(100))
    team_size = db.Column(db.String(20))
    preferred_mbti = db.Column(db.String(100))

    user = db.relationship('User', back_populates='employer_profile')
    vacancies = db.relationship('Vacancy', backref='employer', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry': self.industry,
            'team_size': self.team_size,
            'preferred_mbti': self.preferred_mbti.split(',') if self.preferred_mbti else []
        }

class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer_profiles.id'), nullable=False)  # Явное указание связи
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)  # Добавлено поле даты