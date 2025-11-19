from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import or_, and_
from app import db
from app.models.candidate import CandidateProfile, CandidateVideo
from app.models.vacancy import Vacancy, VacancyResponse
from app.models.user import User
from app.candidate.forms import CandidateProfileForm, AvatarForm, VideoResumeForm
from datetime import datetime
import os
from werkzeug.utils import secure_filename

candidate_bp = Blueprint('candidate', __name__)

# Dashboard и главные страницы
@candidate_bp.route('/candidate/dashboard')
@login_required
def dashboard():
    """Главная страница кандидата"""
    profile = current_user.candidate_profile
    
    # Проверка заполненности профиля
    profile_completion = calculate_completion(profile)
    
    # Получаем параметры фильтрации
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    min_salary = request.args.get('min_salary', '')
    location = request.args.get('location', '')
    employment_type = request.args.get('employment_type', '')
    
    # Базовый запрос активных вакансий
    query = Vacancy.query.filter_by(is_active=True)
    
    # Применяем фильтры
    if search:
        query = query.filter(or_(
            Vacancy.title.ilike(f'%{search}%'),
            Vacancy.description.ilike(f'%{search}%'),
            Vacancy.company.ilike(f'%{search}%'),
            Vacancy.requirements.ilike(f'%{search}%')
        ))
    
    if industry and industry != 'all':
        query = query.filter(Vacancy.industry == industry)
    
    if location:
        query = query.filter(or_(
            Vacancy.location.ilike(f'%{location}%'),
            Vacancy.location == 'Удаленно'
        ))
    
    if min_salary:
        try:
            query = query.filter(Vacancy.salary_range.ilike(f'%{min_salary}%'))
        except ValueError:
            pass
    
    if employment_type and employment_type != 'all':
        if employment_type == 'remote':
            query = query.filter(Vacancy.location.ilike('%удаленно%'))
        elif employment_type == 'office':
            query = query.filter(~Vacancy.location.ilike('%удаленно%'))
        elif employment_type == 'hybrid':
            query = query.filter(Vacancy.location.ilike('%гибрид%'))
    
    # Сортировка по дате создания (новые сначала)
    all_vacancies = query.order_by(Vacancy.created_at.desc()).all()
    
    # Рекомендованные вакансии
    recommended_vacancies = get_recommended_vacancies_for_candidate(profile) if profile else []
    
    # Если есть рекомендованные, добавляем их в начало
    if recommended_vacancies:
        recommended_ids = [v.id for v in recommended_vacancies]
        other_vacancies = [v for v in all_vacancies if v.id not in recommended_ids]
        displayed_vacancies = recommended_vacancies + other_vacancies[:10-len(recommended_vacancies)]
    else:
        displayed_vacancies = all_vacancies[:10]
    
    # Получаем отклики пользователя
    user_responses = VacancyResponse.query.filter_by(candidate_id=current_user.id).all()
    responded_vacancy_ids = [response.vacancy_id for response in user_responses]
    
    # Получаем видео пользователя
    videos = CandidateVideo.query.filter_by(user_id=current_user.id).all()
    
    return render_template('candidate/dashboard.html', 
                         profile=profile,
                         vacancies=displayed_vacancies,
                         recommended_vacancies=recommended_vacancies,
                         profile_completion=profile_completion,
                         responded_vacancy_ids=responded_vacancy_ids,
                         videos=videos,
                         search=search,
                         industry=industry,
                         min_salary=min_salary,
                         location=location,
                         employment_type=employment_type)

@candidate_bp.route('/candidate/profile')
@login_required
def profile():
    """Профиль кандидата"""
    profile = current_user.candidate_profile
    recommended_vacancies = get_recommended_vacancies_for_candidate(profile) if profile else []
    
    # Статистика
    responses_count = VacancyResponse.query.filter_by(candidate_id=current_user.id).count()
    videos_count = CandidateVideo.query.filter_by(user_id=current_user.id).count()
    
    stats = {
        'responses_count': responses_count,
        'videos_count': videos_count,
        'profile_completion': calculate_completion(profile)
    }
    
    return render_template('candidate/profile.html', 
                         profile=profile,
                         recommended_vacancies=recommended_vacancies,
                         stats=stats)

# Вакансии
@candidate_bp.route('/candidate/vacancies')
@login_required
def candidate_vacancies():
    """Просмотр всех вакансий кандидатом"""
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    location = request.args.get('location', '')
    min_salary = request.args.get('min_salary', '')
    employment_type = request.args.get('employment_type', '')
    sort_by = request.args.get('sort_by', 'newest')
    
    query = Vacancy.query.filter_by(is_active=True)
    
    # Применяем фильтры
    if search:
        query = query.filter(or_(
            Vacancy.title.ilike(f'%{search}%'),
            Vacancy.description.ilike(f'%{search}%'),
            Vacancy.company.ilike(f'%{search}%'),
            Vacancy.requirements.ilike(f'%{search}%')
        ))
    
    if industry and industry != 'all':
        query = query.filter(Vacancy.industry == industry)
    
    if location:
        query = query.filter(or_(
            Vacancy.location.ilike(f'%{location}%'),
            Vacancy.location == 'Удаленно'
        ))
    
    if min_salary:
        try:
            query = query.filter(Vacancy.salary_range.ilike(f'%{min_salary}%'))
        except ValueError:
            pass
    
    if employment_type and employment_type != 'all':
        if employment_type == 'remote':
            query = query.filter(Vacancy.location.ilike('%удаленно%'))
        elif employment_type == 'office':
            query = query.filter(~Vacancy.location.ilike('%удаленно%'))
        elif employment_type == 'hybrid':
            query = query.filter(Vacancy.location.ilike('%гибрид%'))
    
    # Сортировка
    if sort_by == 'salary_high':
        query = query.order_by(Vacancy.salary_range.desc())
    elif sort_by == 'salary_low':
        query = query.order_by(Vacancy.salary_range.asc())
    elif sort_by == 'company':
        query = query.order_by(Vacancy.company.asc())
    else:  # newest
        query = query.order_by(Vacancy.created_at.desc())
    
    vacancies = query.all()
    
    # Получаем отклики пользователя
    user_responses = VacancyResponse.query.filter_by(candidate_id=current_user.id).all()
    responded_vacancy_ids = [response.vacancy_id for response in user_responses]
    
    return render_template('candidate/all_vacancies.html', 
                         vacancies=vacancies,
                         responded_vacancy_ids=responded_vacancy_ids,
                         search=search,
                         industry=industry,
                         location=location,
                         min_salary=min_salary,
                         employment_type=employment_type,
                         sort_by=sort_by)

@candidate_bp.route('/candidate/vacancy/<int:vacancy_id>')
@login_required
def vacancy_detail(vacancy_id):
    """Детальная страница вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    # Увеличиваем счетчик просмотров
    vacancy.views = (vacancy.views or 0) + 1
    db.session.commit()
    
    # Проверяем, откликался ли пользователь
    has_responded = VacancyResponse.query.filter_by(
        candidate_id=current_user.id, 
        vacancy_id=vacancy_id
    ).first() is not None
    
    # Получаем рекомендованные вакансии для боковой панели
    profile = current_user.candidate_profile
    recommended_vacancies = get_recommended_vacancies_for_candidate(profile)[:3] if profile else []
    
    return render_template('candidate/vacancy_detail.html',
                         vacancy=vacancy,
                         recommended_vacancies=recommended_vacancies,
                         has_responded=has_responded)

@candidate_bp.route('/candidate/vacancy/<int:vacancy_id>/respond', methods=['POST'])
@login_required
def respond_to_vacancy(vacancy_id):
    """Отклик на вакансию"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    # Проверяем, не откликался ли уже
    existing_response = VacancyResponse.query.filter_by(
        candidate_id=current_user.id,
        vacancy_id=vacancy_id
    ).first()
    
    if existing_response:
        flash('Вы уже откликались на эту вакансию', 'warning')
        return redirect(url_for('candidate.vacancy_detail', vacancy_id=vacancy_id))
    
    # Создаем отклик
    response = VacancyResponse(
        candidate_id=current_user.id,
        vacancy_id=vacancy_id,
        status='pending',
        responded_at=datetime.utcnow()
    )
    
    db.session.add(response)
    db.session.commit()
    
    flash('Отклик успешно отправлен!', 'success')
    return redirect(url_for('candidate.vacancy_detail', vacancy_id=vacancy_id))

# Отклики и видео
@candidate_bp.route('/candidate/responses')
@login_required
def my_responses():
    """Мои отклики"""
    responses = VacancyResponse.query.filter_by(candidate_id=current_user.id)\
        .order_by(VacancyResponse.responded_at.desc())\
        .all()
    
    return render_template('candidate/my_responses.html', responses=responses)

@candidate_bp.route('/candidate/videos')
@login_required
def my_videos():
    """Мои видеовизитки"""
    videos = CandidateVideo.query.filter_by(user_id=current_user.id)\
        .order_by(CandidateVideo.created_at.desc())\
        .all()
    
    return render_template('candidate/my_videos.html', videos=videos)

# Настройки и профиль
@candidate_bp.route('/candidate/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Настройки профиля кандидата"""
    profile = current_user.candidate_profile
    if profile is None:
        profile = CandidateProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()
    
    form = CandidateProfileForm(obj=profile)
    
    if form.validate_on_submit():
        # Update the profile with form data
        form.populate_obj(profile)
        db.session.commit()
        flash('Настройки успешно сохранены', 'success')
        return redirect(url_for('candidate.profile'))
    
    return render_template('candidate/settings.html', form=form)

@candidate_bp.route('/candidate/settings/avatar', methods=['GET', 'POST'])
@login_required
def avatar_settings():
    """Настройки аватара"""
    form = AvatarForm()
    
    if form.validate_on_submit():
        if form.avatar.data:
            avatar = form.avatar.data.read()
            mimetype = form.avatar.data.mimetype
            current_user.avatar = avatar
            current_user.avatar_mimetype = mimetype
            db.session.commit()
            flash('Аватар успешно обновлен', 'success')
        return redirect(url_for('candidate.profile'))
    
    return render_template('candidate/avatar_settings.html', form=form)

@candidate_bp.route('/candidate/settings/video', methods=['GET', 'POST'])
@login_required
def video_settings():
    """Настройки видеовизитки"""
    form = VideoResumeForm()
    
    if form.validate_on_submit():
        if form.video_resume.data:
            video_file = form.video_resume.data
            filename = secure_filename(video_file.filename)
            
            # Создаем папку если не существует
            upload_folder = os.path.join('app', 'static', 'uploads', 'videos')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Сохраняем видео
            video_path = os.path.join(upload_folder, filename)
            video_file.save(video_path)
            
            # Создаем запись в базе
            video = CandidateVideo(
                user_id=current_user.id,
                filename=filename,
                filepath=video_path
            )
            
            db.session.add(video)
            db.session.commit()
            
            flash('Видеовизитка успешно загружена', 'success')
        return redirect(url_for('candidate.profile'))
    
    return render_template('candidate/video_settings.html', form=form)

# Аналитика и статистика
@candidate_bp.route('/candidate/analytics')
@login_required
def analytics():
    """Аналитика профиля"""
    profile = current_user.candidate_profile
    
    # Статистика откликов
    responses = VacancyResponse.query.filter_by(candidate_id=current_user.id).all()
    total_responses = len(responses)
    pending_responses = len([r for r in responses if r.status == 'pending'])
    accepted_responses = len([r for r in responses if r.status == 'accepted'])
    rejected_responses = len([r for r in responses if r.status == 'rejected'])
    
    stats = {
        'total_responses': total_responses,
        'pending_responses': pending_responses,
        'accepted_responses': accepted_responses,
        'rejected_responses': rejected_responses,
        'response_rate': (accepted_responses / total_responses * 100) if total_responses > 0 else 0
    }
    
    # Рекомендации по улучшению профиля
    recommendations = get_profile_recommendations(profile)
    
    return render_template('candidate/analytics.html',
                         stats=stats,
                         recommendations=recommendations,
                         profile_completion=calculate_completion(profile))

# Вспомогательные функции
def get_recommended_vacancies_for_candidate(candidate_profile):
    """Получить рекомендованные вакансии для кандидата"""
    if not candidate_profile:
        return []
    
    # Получаем все активные вакансии
    all_vacancies = Vacancy.query.filter_by(is_active=True).all()
    
    recommended = []
    
    for vacancy in all_vacancies:
        score = calculate_candidate_match_score(candidate_profile, vacancy)
        if score > 0.3:  # Порог совпадения 30%
            recommended.append((vacancy, score))
    
    # Сортируем по убыванию релевантности
    recommended.sort(key=lambda x: x[1], reverse=True)
    
    return [vacancy for vacancy, score in recommended[:5]]

def calculate_candidate_match_score(candidate_profile, vacancy):
    """Рассчитать степень совпадения профиля кандидата с вакансией"""
    score = 0
    max_score = 0
    
    # Совпадение по профессии/специальности
    if candidate_profile.profession and vacancy.title:
        max_score += 1
        candidate_profession_lower = candidate_profile.profession.lower()
        vacancy_title_lower = vacancy.title.lower()
        
        # Простая проверка на совпадение ключевых слов
        if any(keyword in vacancy_title_lower for keyword in candidate_profession_lower.split()):
            score += 1
    
    # Совпадение по навыкам
    if candidate_profile.skills and vacancy.requirements:
        max_score += 1
        candidate_skills = [skill.strip().lower() for skill in candidate_profile.skills.split(',')]
        vacancy_requirements = vacancy.requirements.lower()
        
        matching_skills = sum(1 for skill in candidate_skills if skill in vacancy_requirements)
        if matching_skills > 0:
            score += matching_skills / len(candidate_skills)
    
    # Совпадение по MBTI
    if candidate_profile.mbti_type and vacancy.required_mbti:
        max_score += 1
        vacancy_mbti = [mbti.strip().upper() for mbti in vacancy.required_mbti.split(',')]
        
        if candidate_profile.mbti_type.upper() in vacancy_mbti:
            score += 1
    
    # Совпадение по опыту
    if candidate_profile.experience is not None:
        max_score += 0.5
        # Простая логика: если опыт кандидата >= 2 лет, подходит для большинства вакансий
        if candidate_profile.experience >= 2:
            score += 0.5
    
    return score / max_score if max_score > 0 else 0

def calculate_completion(profile):
    """Рассчитать процент заполненности профиля"""
    if not profile:
        return 0
        
    fields = [
        profile.profession,
        profile.experience is not None,
        profile.skills,
        profile.mbti_type,
        profile.field,
        current_user.avatar is not None
    ]
    
    filled = sum(1 for field in fields if field)
    return int((filled / len(fields)) * 100) if fields else 0

def get_profile_recommendations(profile):
    """Получить рекомендации по улучшению профиля"""
    recommendations = []
    
    if not profile:
        recommendations.append("Заполните базовую информацию о себе")
        return recommendations
    
    if not profile.profession:
        recommendations.append("Укажите вашу профессию")
    
    if not profile.experience:
        recommendations.append("Укажите ваш опыт работы")
    
    if not profile.skills:
        recommendations.append("Добавьте ключевые навыки")
    
    if not profile.mbti_type:
        recommendations.append("Пройдите MBTI-тест для лучшего подбора")
    
    if not current_user.avatar:
        recommendations.append("Добавьте аватар для лучшего восприятия")
    
    if len(recommendations) == 0:
        recommendations.append("Ваш профиль выглядит отлично! Продолжайте в том же духе.")
    
    return recommendations