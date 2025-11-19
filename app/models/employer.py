from datetime import datetime
from app.extensions import db

class EmployerProfile(db.Model):
    __tablename__ = 'employer_profiles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    company_name = db.Column(db.String(100), unique=True, nullable=False)
    company_description = db.Column(db.Text)
    industry = db.Column(db.String(50))
    website = db.Column(db.String(200))
    team_size = db.Column(db.String(20))
    preferred_mbti = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('employer_profile', uselist=False))
    employer_vacancies = db.relationship('Vacancy', backref='employer_profile_obj', lazy=True)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'company_name': self.company_name,
            'company_description': self.company_description,
            'industry': self.industry,
            'website': self.website,
            'team_size': self.team_size,
            'preferred_mbti': self.preferred_mbti
        }