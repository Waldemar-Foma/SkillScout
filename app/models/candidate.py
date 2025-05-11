from datetime import datetime
from app.main import db

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    profession = db.Column(db.String(100))
    experience = db.Column(db.Integer)  # in years
    skills = db.Column(db.Text)
    video_resume = db.Column(db.String(255))
    mbti_type = db.Column(db.String(4))
    big_five = db.Column(db.JSON)  # JSON with traits scores
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # AI analysis results
    speech_analysis = db.Column(db.JSON)
    emotion_analysis = db.Column(db.JSON)
    compatibility_stats = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.user.name,
            'profession': self.profession,
            'experience': self.experience,
            'skills': self.skills.split(',') if self.skills else [],
            'video_resume': self.video_resume,
            'mbti': self.mbti_type,
            'big_five': self.big_five or {},
            'analysis': {
                'speech': self.speech_analysis or {},
                'emotion': self.emotion_analysis or {}
            }
        }
    
    def update_compatibility(self):
        # Method to recalculate compatibility with vacancies
        pass