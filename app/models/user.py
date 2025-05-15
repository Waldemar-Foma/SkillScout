from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
from typing import Optional


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='candidate')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(
        db.DateTime, 
        default=db.func.current_timestamp(),
        onupdate=db.func.current_timestamp()
    )

    def __repr__(self):
        return f'<User {self.email}>'

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in: int = 3600) -> str:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    @staticmethod
    def verify_reset_password_token(token: str) -> Optional['User']:
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=3600)['user_id']
            return User.query.get(user_id)
        except (TypeError, ValueError, KeyError):
            return None
