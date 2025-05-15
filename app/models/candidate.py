from app.extensions import db

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    profession = db.Column(db.String(100))
    experience = db.Column(db.Integer)
    skills = db.Column(db.Text)
    mbti_type = db.Column(db.String(10))
    video_resume = db.Column(db.String(255))

    def __repr__(self):
        return f'<CandidateProfile {self.id}>'