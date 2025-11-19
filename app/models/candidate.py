from datetime import datetime
from app.extensions import db

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    profession = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    skills = db.Column(db.Text)
    mbti_type = db.Column(db.String(4))
    field = db.Column(db.String(50))
    video_resume = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('candidate_profile', uselist=False))
    candidate_responses = db.relationship('VacancyResponse', backref='candidate_profile_obj', lazy=True)
    
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'profession': self.profession,
            'experience': self.experience,
            'skills': self.skills,
            'mbti_type': self.mbti_type,
            'field': self.field,
            'video_resume': self.video_resume
        }


class CandidateVideo(db.Model):
    __tablename__ = 'candidate_videos'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    analysis = db.Column(db.Text)  # JSON analysis results
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref=db.backref('videos', lazy=True))
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'filepath': self.filepath,
            'analysis': self.analysis,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }