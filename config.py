import os
from dotenv import load_dotenv

load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('AXL_AXL_AXL') or 'dev-key-123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'instance', 'db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    
    # Настройки видео
    VIDEO_UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'videos')
    UPLOAD_FOLDER = os.path.join(basedir, 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'mov', 'avi'}
    MAX_VIDEO_SIZE = 100 * 1024 * 1024  # 100MB
    
    # Настройки почты
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465  # SSL (безопаснее)
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'aricayrapetyan@yandex.ru'
    MAIL_PASSWORD = 'squcpcjsepdhbfkd'
    MAIL_DEFAULT_SENDER = 'aricayrapetyan@yandex.ru'