from datetime import datetime
from app.main import db

class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('employer_profiles.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    location = db.Column(db.String(100))
    salary_range = db.Column(db.String(50))
    is_remote = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='active')  # active, archived
    
    # Psychological preferences
    required_mbti = db.Column(db.String(100))
    required_big_five = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'company': self.employer.company_name,
            'location': self.location,
            'salary_range': self.salary_range,
            'is_remote': self.is_remote,
            'requirements': self.requirements,
            'psychological_profile': {
                'mbti': self.required_mbti.split(',') if self.required_mbti else [],
                'big_five': self.required_big_five or {}
            }
        }