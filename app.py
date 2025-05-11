import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import speech_recognition as sr
from moviepy.editor import VideoFileClip
import re
from collections import defaultdict

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['AVATARS_FOLDER'] = 'static/uploads/avatars'
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'avi', 'jpg', 'jpeg', 'png'}
app.config['MAX_AVATAR_SIZE'] = 2 * 1024 * 1024  # 2MB

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    avatar = db.Column(db.String(200), default='default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CandidateProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    video_path = db.Column(db.String(200))
    audio_path = db.Column(db.String(200))
    transcript = db.Column(db.Text)
    ocean_scores = db.Column(db.JSON)
    mbti_type = db.Column(db.String(4))
    analysis_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_audio(video_path):
    try:
        video = VideoFileClip(video_path)
        audio_filename = f"audio_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_filename)
        video.audio.write_audiofile(audio_path)
        video.close()
        return audio_path
    except Exception as e:
        app.logger.error(f"Error extracting audio: {str(e)}")
        return None

def audio_to_text(audio_path):
    try:
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="ru-RU")
        return text
    except Exception as e:
        app.logger.error(f"Error converting audio to text: {str(e)}")
        return None

def analyze_personality(text):
    openness_keywords = {
        'творческий': 0.8, 'воображение': 0.7, 'искусство': 0.7, 'любопытный': 0.6,
        'приключения': 0.7, 'инновационный': 0.7, 'оригинальный': 0.6, 'разнообразие': 0.5,
        'изменения': 0.5, 'исследовать': 0.6
    }
    
    conscientiousness_keywords = {
        'организованный': 0.8, 'ответственный': 0.7, 'надежный': 0.7, 'трудолюбивый': 0.6,
        'дисциплинированный': 0.8, 'эффективный': 0.6, 'тщательный': 0.5, 'осторожный': 0.5,
        'план': 0.6, 'дедлайн': 0.5
    }
    
    extraversion_keywords = {
        'общительный': 0.8, 'энергичный': 0.7, 'коммуникабельный': 0.7, 'разговорчивый': 0.6,
        'друг': 0.5, 'люди': 0.4, 'вечеринка': 0.6, 'социальный': 0.5,
        'группа': 0.4, 'активный': 0.5
    }
    
    agreeableness_keywords = {
        'добрый': 0.8, 'сочувствующий': 0.8, 'помогающий': 0.7, 'кооперативный': 0.6,
        'доверчивый': 0.5, 'честный': 0.6, 'скромный': 0.5, 'сопереживающий': 0.7,
        'поддержка': 0.5, 'забота': 0.5
    }
    
    neuroticism_keywords = {
        'тревожный': 0.8, 'беспокойство': 0.7, 'нервный': 0.7, 'стресс': 0.6,
        'перепады настроения': 0.6, 'неуверенный': 0.7, 'страх': 0.6, 'злой': 0.5,
        'расстроенный': 0.5, 'напряженный': 0.6
    }
    
    trait_scores = defaultdict(float)
    trait_counts = defaultdict(int)
    
    words = re.findall(r'\b\w+\b', text.lower())
    
    for word in words:
        if word in openness_keywords:
            trait_scores['openness'] += openness_keywords[word]
            trait_counts['openness'] += 1
        if word in conscientiousness_keywords:
            trait_scores['conscientiousness'] += conscientiousness_keywords[word]
            trait_counts['conscientiousness'] += 1
        if word in extraversion_keywords:
            trait_scores['extraversion'] += extraversion_keywords[word]
            trait_counts['extraversion'] += 1
        if word in agreeableness_keywords:
            trait_scores['agreeableness'] += agreeableness_keywords[word]
            trait_counts['agreeableness'] += 1
        if word in neuroticism_keywords:
            trait_scores['neuroticism'] += neuroticism_keywords[word]
            trait_counts['neuroticism'] += 1
    
    ocean_scores = {}
    for trait in ['openness', 'conscientiousness', 'extraversion', 'agreeableness', 'neuroticism']:
        if trait_counts[trait] > 0:
            ocean_scores[trait] = min(1.0, trait_scores[trait] / trait_counts[trait])
        else:
            ocean_scores[trait] = 0.5
    
    return ocean_scores

def ocean_to_mbti(ocean_scores):
    ei = 'E' if ocean_scores['extraversion'] >= 0.5 else 'I'
    ns = 'N' if ocean_scores['openness'] >= 0.6 else 'S'
    ft = 'F' if ocean_scores['agreeableness'] >= 0.55 else 'T'
    jp = 'J' if ocean_scores['conscientiousness'] >= 0.5 else 'P'
    return f"{ei}{ns}{ft}{jp}"

def generate_analysis(ocean_scores, mbti_type, transcript):
    ocean_descriptions = {
        'openness': {
            'low': "Вы предпочитаете традиционные подходы и проверенные методы.",
            'medium': "Вы открыты новому, но цените стабильность.",
            'high': "Вы очень открыты новому, креативны и любознательны."
        },
        'conscientiousness': {
            'low': "Вы гибки в планировании и предпочитаете спонтанность.",
            'medium': "Вы организованы, но можете адаптироваться к изменениям.",
            'high': "Вы очень организованы, дисциплинированы и надежны."
        },
        'extraversion': {
            'low': "Вы интроверт, предпочитаете уединение и глубокие размышления.",
            'medium': "Вы амбиверт, комфортно чувствуете себя как в компании, так и в одиночестве.",
            'high': "Вы экстраверт, получаете энергию от общения и социальных взаимодействий."
        },
        'agreeableness': {
            'low': "Вы прямолинейны и цените честность выше дипломатии.",
            'medium': "Вы доброжелательны, но можете отстаивать свою позицию.",
            'high': "Вы очень доброжелательны, сопереживаете другим и стремитесь к гармонии."
        },
        'neuroticism': {
            'low': "Вы эмоционально стабильны и спокойны в стрессовых ситуациях.",
            'medium': "Вы обычно спокойны, но можете переживать в сложных ситуациях.",
            'high': "Вы эмоционально чувствительны и остро реагируете на стресс."
        }
    }
    
    mbti_full_descriptions = {
        'INTJ': ("Стратег (INTJ)", "Аналитичный, решительный, инновационный."),
        'INTP': ("Логик (INTP)", "Изобретательный, любознательный, теоретик."),
        'ENTJ': ("Командир (ENTJ)", "Харизматичный, уверенный, лидер."),
        'ENTP': ("Полемист (ENTP)", "Умный, любознательный, изобретательный."),
        'INFJ': ("Активист (INFJ)", "Творческий, вдохновляющий, решительный."),
        'INFP': ("Посредник (INFP)", "Идеалистичный, альтруистичный, чуткий."),
        'ENFJ': ("Тренер (ENFJ)", "Харизматичный, убедительный, общительный."),
        'ENFP': ("Борец за свободу (ENFP)", "Энтузиаст, творческий, общительный."),
        'ISTJ': ("Администратор (ISTJ)", "Практичный, ответственный, надежный."),
        'ISFJ': ("Защитник (ISFJ)", "Заботливый, преданный, внимательный."),
        'ESTJ': ("Менеджер (ESTJ)", "Организованный, практичный, решительный."),
        'ESFJ': ("Консул (ESFJ)", "Дружелюбный, ответственный, общительный."),
        'ISTP': ("Виртуоз (ISTP)", "Спонтанный, технически подкованный, решительный."),
        'ISFP': ("Артист (ISFP)", "Чуткий, творческий, гибкий."),
        'ESTP': ("Делец (ESTP)", "Энергичный, проницательный, предприимчивый."),
        'ESFP': ("Развлекатель (ESFP)", "Спонтанный, энергичный, дружелюбный.")
    }
    
    ocean_analysis = []
    for trait, score in ocean_scores.items():
        if score < 0.4:
            desc = ocean_descriptions[trait]['low']
        elif score < 0.7:
            desc = ocean_descriptions[trait]['medium']
        else:
            desc = ocean_descriptions[trait]['high']
        ocean_analysis.append(f"<b>{trait.capitalize()}</b> ({score:.2f}): {desc}")
    
    mbti_name, mbti_desc = mbti_full_descriptions.get(mbti_type, ("Неизвестный тип", "Описание недоступно"))
    
    recommendations = []
    if ocean_scores['openness'] < 0.4:
        recommendations.append("Попробуйте что-то новое - это расширит ваш кругозор.")
    if ocean_scores['conscientiousness'] < 0.4:
        recommendations.append("Планирование поможет вам быть более продуктивным.")
    if ocean_scores['extraversion'] < 0.4:
        recommendations.append("Социальные взаимодействия могут быть полезны для вашего развития.")
    if ocean_scores['agreeableness'] < 0.4:
        recommendations.append("Умение находить компромиссы поможет в работе в команде.")
    if ocean_scores['neuroticism'] > 0.6:
        recommendations.append("Техники релаксации помогут вам справляться со стрессом.")
    
    analysis_text = (
        f"<h3>Ваш психологический портрет</h3>"
        f"<p><b>Тип личности:</b> {mbti_name}<br>{mbti_desc}</p>"
        f"<h3>Черты личности (OCEAN модель)</h3>"
        f"<ul><li>" + "</li><li>".join(ocean_analysis) + "</li></ul>"
        f"<h3>Рекомендации</h3>"
        f"<ul><li>" + "</li><li>".join(recommendations if recommendations else ["Ваш профиль сбалансирован, продолжайте развиваться!"]) + "</li></ul>"
        f"<h3>Распознанный текст</h3>"
        f"<p>{transcript[:500]}" + ("..." if len(transcript) > 500 else "") + "</p>"
    )
    
    return analysis_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        user_type = request.form.get('user_type')
        
        if User.query.filter_by(email=email).first():
            flash('Email уже зарегистрирован', 'error')
            return redirect(url_for('register'))
        
        user = User(
            email=email,
            name=name,
            password=generate_password_hash(password),
            user_type=user_type
        )
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Неверный email или пароль', 'error')
    
    return render_template('auth/login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.user_type == 'candidate':
        profile = CandidateProfile.query.filter_by(user_id=current_user.id).first()
        return render_template('candidate/dashboard.html', profile=profile)
    else:
        candidates = CandidateProfile.query.all()
        return render_template('candidates/dashboard.html', candidates=candidates)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_video():
    if current_user.user_type != 'candidate':
        flash('Только кандидаты могут загружать видео', 'error')
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('Файл не выбран', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(f"{current_user.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
            video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(video_path)
            
            audio_path = extract_audio(video_path)
            if not audio_path:
                flash('Ошибка при извлечении аудио', 'error')
                return redirect(request.url)
            
            text = audio_to_text(audio_path)
            if not text:
                flash('Ошибка при преобразовании аудио в текст', 'error')
                return redirect(request.url)
            
            ocean_scores = analyze_personality(text)
            mbti_type = ocean_to_mbti(ocean_scores)
            analysis_text = generate_analysis(ocean_scores, mbti_type, text)
            
            profile = CandidateProfile(
                user_id=current_user.id,
                video_path=video_path,
                audio_path=audio_path,
                transcript=text,
                ocean_scores=ocean_scores,
                mbti_type=mbti_type,
                analysis_text=analysis_text
            )
            db.session.add(profile)
            db.session.commit()
            
            return redirect(url_for('analysis', profile_id=profile.id))
    
    return render_template('candidate/upload.html')

@app.route('/profile/<int:user_id>')
@login_required
def profile(user_id):
    user = User.query.get_or_404(user_id)
    profile = CandidateProfile.query.filter_by(user_id=user_id).first()
    
    if current_user.user_type != 'employer' and current_user.id != user_id:
        flash('У вас нет доступа к этому профилю', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('profile.html', user=user, profile=profile)

@app.route('/analysis/<int:profile_id>')
@login_required
def analysis(profile_id):
    profile = CandidateProfile.query.get_or_404(profile_id)
    if current_user.id != profile.user_id and current_user.user_type != 'employer':
        flash('Нет доступа', 'error')
        return redirect(url_for('dashboard'))
    
    return render_template('analysis.html',
                         profile=profile,
                         ocean_scores=profile.ocean_scores,
                         mbti_type=profile.mbti_type,
                         analysis_text=profile.analysis_text)

@app.route('/candidates')
@login_required
def candidates():
    if current_user.user_type != 'employer':
        flash('Только работодатели могут просматривать кандидатов', 'error')
        return redirect(url_for('dashboard'))
    
    mbti_types = ['INTJ', 'INTP', 'ENTJ', 'ENTP', 'INFJ', 'INFP', 
                 'ENFJ', 'ENFP', 'ISTJ', 'ISFJ', 'ESTJ', 'ESFJ', 
                 'ISTP', 'ISFP', 'ESTP', 'ESFP']
    
    query = CandidateProfile.query.join(User)
    
    mbti_filter = request.args.get('mbti')
    if mbti_filter:
        query = query.filter(CandidateProfile.mbti_type == mbti_filter)
    
    min_openness = request.args.get('min_openness', type=float)
    if min_openness is not None:
        query = query.filter(CandidateProfile.ocean_scores['openness'].astext.cast(db.Float) >= min_openness)
    
    candidates = query.all()
    
    return render_template('candidates.html', 
                         candidates=candidates,
                         mbti_types=mbti_types)

@app.route('/candidate/<int:candidate_id>')
@login_required
def view_candidate(candidate_id):
    if current_user.user_type != 'employer':
        flash('Только работодатели могут просматривать профили', 'error')
        return redirect(url_for('dashboard'))
    
    profile = CandidateProfile.query.get_or_404(candidate_id)
    return render_template('candidate_profile.html', profile=profile)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()
        db.create_all()
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(app.config['AVATARS_FOLDER'], exist_ok=True)
        
        default_avatar_path = os.path.join(app.config['AVATARS_FOLDER'], 'default.png')
        if not os.path.exists(default_avatar_path):
            with open(default_avatar_path, 'wb') as f:
                f.write(b'')
    
    app.run(debug=True)