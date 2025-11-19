from datetime import datetime
from app.extensions import db

class Vacancy(db.Model):
    __tablename__ = 'vacancy'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer_profiles.user_id'))
    title = db.Column(db.String(100))
    company = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    industry = db.Column(db.String(50))
    salary_range = db.Column(db.String(50))
    stress = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    required_mbti = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    
    # Relationships
    vacancy_responses = db.relationship('VacancyResponse', backref='vacancy_obj', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'company': self.company,
            'location': self.location,
            'salary_range': self.salary_range,
            'requirements': self.requirements,
            'psychological_profile': {
                'mbti': self.required_mbti.split(',') if self.required_mbti else [],
            }
        }


class VacancyResponse(db.Model):
    __tablename__ = 'vacancy_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.user_id'), nullable=False)
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancy.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, accepted, rejected, interview
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)
    employer_notes = db.Column(db.Text, nullable=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'candidate_id': self.candidate_id,
            'vacancy_id': self.vacancy_id,
            'status': self.status,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None,
            'employer_notes': self.employer_notes
        }