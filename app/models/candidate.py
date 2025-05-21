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

    user = db.relationship('User', back_populates='candidate_profile')

    def __repr__(self):
        return f'<CandidateProfile {self.id}>'

class CandidateVideo(db.Model):
    __tablename__ = 'candidate_videos'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    filename = db.Column(db.String(255))
    filepath = db.Column(db.String(255))
    analysis = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=db.func.now())
    status = db.Column(db.String(20), default='uploaded')

    def __repr__(self):
        return f'<CandidateVideo {self.id}>'