from datetime import datetime
from app.main import db
from ..extensions import db

class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    company_name = db.Column(db.String(100))
    company_description = db.Column(db.Text)
    company_logo = db.Column(db.String(255))
    industry = db.Column(db.String(50))
    website = db.Column(db.String(100))
    team_size = db.Column(db.String(20))  # 1-10, 11-50, etc.
    preferred_mbti = db.Column(db.String(100))  # Comma-separated MBTI types
    
    vacancies = db.relationship('Vacancy', backref='employer', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'industry': self.industry,
            'team_size': self.team_size,
            'preferred_mbti': self.preferred_mbti.split(',') if self.preferred_mbti else []
        }