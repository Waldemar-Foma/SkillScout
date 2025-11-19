from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'candidate' or 'employer'
    fullname = db.Column(db.String(100))
    company_name = db.Column(db.String(100))
    field = db.Column(db.String(50))
    experience = db.Column(db.Integer)
    skills = db.Column(db.Text)
    avatar = db.Column(db.LargeBinary)
    avatar_mimetype = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_id(self):
        return str(self.id)
    
    def check_password(self, password):
        # Implement password checking logic
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_candidate(self):
        return self.role == 'candidate'
    
    @property
    def is_employer(self):
        return self.role == 'employer'
    
    def get_or_create_profile(self):
        if self.role == 'candidate':
            if not self.candidate_profile:
                from app.models.candidate import CandidateProfile
                profile = CandidateProfile(user_id=self.id)
                db.session.add(profile)
                db.session.commit()
            return self.candidate_profile
        elif self.role == 'employer':
            if not self.employer_profile:
                from app.models.employer import EmployerProfile
                profile = EmployerProfile(user_id=self.id, company_name=self.company_name or '')
                db.session.add(profile)
                db.session.commit()
            return self.employer_profile
        return None