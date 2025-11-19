from flask import render_template, request, redirect, url_for, flash, Blueprint, jsonify
from flask_login import login_required, current_user
from sqlalchemy import or_, and_, func
from app import db
from app.models.employer import EmployerProfile
from app.models.vacancy import Vacancy, VacancyResponse
from app.models.candidate import CandidateProfile
from app.models.user import User
from app.employer.forms import VacancyForm, EmployerProfileForm, AvatarForm
from datetime import datetime, timedelta

employer_bp = Blueprint('employer', __name__)

# Dashboard и главные страницы
@employer_bp.route('/employer/dashboard')
@login_required
def dashboard():
    """Главная страница работодателя"""
    # Собственные вакансии работодателя
    active_vacancies = Vacancy.query.filter_by(
        employer_id=current_user.id, 
        is_active=True
    ).order_by(Vacancy.created_at.desc()).all()
    
    archived_vacancies = Vacancy.query.filter_by(
        employer_id=current_user.id, 
        is_active=False
    ).order_by(Vacancy.created_at.desc()).all()
    
    # Рекомендованные вакансии для работодателя
    employer_profile = current_user.employer_profile
    recommended_vacancies = get_recommended_vacancies(employer_profile)
    
    # Статистика
    total_responses = VacancyResponse.query\
        .join(Vacancy)\
        .filter(Vacancy.employer_id == current_user.id)\
        .count()
    
    recent_responses = VacancyResponse.query\
        .join(Vacancy)\
        .filter(Vacancy.employer_id == current_user.id)\
        .filter(VacancyResponse.responded_at >= datetime.utcnow() - timedelta(days=7))\
        .count()
    
    stats = {
        'active_count': len(active_vacancies),
        'archived_count': len(archived_vacancies),
        'total_responses': total_responses,
        'recent_responses': recent_responses,
        'total_views': sum((v.views or 0) for v in active_vacancies),
        'profile_completion': calculate_employer_completion(employer_profile)
    }
    
    # Последние отклики
    recent_responses_list = VacancyResponse.query\
        .join(Vacancy)\
        .join(CandidateProfile, VacancyResponse.candidate_id == CandidateProfile.user_id)\
        .join(User, CandidateProfile.user_id == User.id)\
        .filter(Vacancy.employer_id == current_user.id)\
        .order_by(VacancyResponse.responded_at.desc())\
        .limit(5)\
        .all()
    
    return render_template(
        'employer/dashboard.html',
        active_vacancies=active_vacancies,
        archived_vacancies=archived_vacancies,
        recommended_vacancies=recommended_vacancies,
        recent_responses=recent_responses_list,
        stats=stats
    )

@employer_bp.route('/employer/profile')
@login_required
def profile():
    """Профиль работодателя"""
    profile = current_user.employer_profile
    recommended_vacancies = get_recommended_vacancies(profile) if profile else []
    
    # Статистика компании
    active_vacancies_count = Vacancy.query.filter_by(
        employer_id=current_user.id, 
        is_active=True
    ).count()
    
    total_responses = VacancyResponse.query\
        .join(Vacancy)\
        .filter(Vacancy.employer_id == current_user.id)\
        .count()
    
    stats = {
        'active_vacancies': active_vacancies_count,
        'total_responses': total_responses,
        'profile_completion': calculate_employer_completion(profile)
    }
    
    # Добавляем форму для загрузки аватара
    form = AvatarForm()
    
    return render_template('employer/profile.html',
                         profile=profile,
                         recommended_vacancies=recommended_vacancies,
                         stats=stats,
                         form=form)

# Управление вакансиями
@employer_bp.route('/employer/vacancies')
@login_required
def all_vacancies():
    """Просмотр всех вакансий с фильтрами"""
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    location = request.args.get('location', '')
    salary_range = request.args.get('salary_range', '')
    sort_by = request.args.get('sort_by', 'newest')
    
    query = Vacancy.query.filter_by(is_active=True)
    
    # Исключаем вакансии текущего работодателя
    query = query.filter(Vacancy.employer_id != current_user.id)
    
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
    
    if salary_range:
        try:
            query = query.filter(Vacancy.salary_range.ilike(f'%{salary_range}%'))
        except ValueError:
            pass
    
    # Сортировка
    if sort_by == 'salary_high':
        query = query.order_by(Vacancy.salary_range.desc())
    elif sort_by == 'salary_low':
        query = query.order_by(Vacancy.salary_range.asc())
    elif sort_by == 'views':
        query = query.order_by(Vacancy.views.desc())
    else:  # newest
        query = query.order_by(Vacancy.created_at.desc())
    
    vacancies = query.all()
    
    return render_template('employer/all_vacancies.html', 
                         vacancies=vacancies,
                         search=search,
                         industry=industry,
                         location=location,
                         salary_range=salary_range,
                         sort_by=sort_by)

@employer_bp.route('/vacancy/new', methods=['GET', 'POST'])
@login_required
def new_vacancy():
    """Создание новой вакансии"""
    form = VacancyForm()
    
    # Устанавливаем компанию по умолчанию
    if current_user.company_name:
        form.company.data = current_user.company_name

    if form.validate_on_submit():
        # Проверка зарплаты
        salary_warning = check_salary_range(form.salary_range.data, form.title.data, form.industry.data)
        
        # Создаем новую вакансию
        vacancy = Vacancy(
            employer_id=current_user.id,
            title=form.title.data,
            company=form.company.data,
            description=form.description.data,
            requirements=form.requirements.data,
            location=form.location.data,
            industry=form.industry.data,
            salary_range=form.salary_range.data,
            required_mbti=form.required_mbti.data,
            stress=form.stress.data if form.stress.data else None,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        db.session.add(vacancy)
        db.session.commit()
        
        if salary_warning:
            flash(f'Вакансия создана! {salary_warning}', 'warning')
        else:
            flash('Вакансия успешно создана', 'success')
            
        return redirect(url_for('employer.dashboard'))
    
    # Передаем данные о рыночных зарплатах для подсказок
    market_data = get_market_salary_data()
    return render_template('employer/vacancy.html', form=form, market_data=market_data)

@employer_bp.route('/employer/vacancy/<int:vacancy_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vacancy(vacancy_id):
    """Редактирование вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    # Проверяем, что вакансия принадлежит текущему пользователю
    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для редактирования этой вакансии', 'danger')
        return redirect(url_for('employer.dashboard'))
    
    form = VacancyForm(obj=vacancy)
        
    if form.validate_on_submit():
        form.populate_obj(vacancy)
        db.session.commit()
        flash('Вакансия успешно обновлена', 'success')
        return redirect(url_for('employer.dashboard'))
    
    return render_template('employer/edit_vacancy.html', form=form, vacancy=vacancy)

@employer_bp.route('/vacancy/archive/<int:vacancy_id>', methods=['POST'])
@login_required
def archive_vacancy(vacancy_id):
    """Архивация вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для архивации этой вакансии', 'danger')
        return redirect(url_for('employer.dashboard'))
    
    vacancy.is_active = False
    db.session.commit()
    
    flash('Вакансия перемещена в архив', 'success')
    return redirect(url_for('employer.dashboard'))

@employer_bp.route('/vacancy/restore/<int:vacancy_id>', methods=['POST'])
@login_required
def restore_vacancy(vacancy_id):
    """Восстановление вакансии из архива"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для восстановления этой вакансии', 'danger')
        return redirect(url_for('employer.dashboard'))
    
    vacancy.is_active = True
    db.session.commit()
    
    flash('Вакансия восстановлена', 'success')
    return redirect(url_for('employer.dashboard'))

@employer_bp.route('/vacancy/delete/<int:vacancy_id>', methods=['POST'])
@login_required
def delete_vacancy(vacancy_id):
    """Удаление вакансии"""
    vacancy = Vacancy.query.get_or_404(vacancy_id)
    
    if vacancy.employer_id != current_user.id:
        flash('У вас нет прав для удаления этой вакансии', 'danger')
        return redirect(url_for('employer.dashboard'))
    
    # Удаляем связанные отклики
    VacancyResponse.query.filter_by(vacancy_id=vacancy_id).delete()
    
    db.session.delete(vacancy)
    db.session.commit()
    
    flash('Вакансия удалена', 'success')
    return redirect(url_for('employer.dashboard'))

# Управление откликами
@employer_bp.route('/employer/responses')
@login_required
def vacancy_responses():
    """Просмотр всех откликов на вакансии"""
    responses = VacancyResponse.query\
        .join(Vacancy)\
        .join(CandidateProfile, VacancyResponse.candidate_id == CandidateProfile.user_id)\
        .join(User, CandidateProfile.user_id == User.id)\
        .filter(Vacancy.employer_id == current_user.id)\
        .order_by(VacancyResponse.responded_at.desc())\
        .all()
    
    return render_template('employer/vacancy_responses.html', responses=responses)

@employer_bp.route('/employer/response/<int:response_id>')
@login_required
def response_detail(response_id):
    """Детальная информация об отклике"""
    response = VacancyResponse.query\
        .join(Vacancy)\
        .join(CandidateProfile, VacancyResponse.candidate_id == CandidateProfile.user_id)\
        .join(User, CandidateProfile.user_id == User.id)\
        .filter(VacancyResponse.id == response_id)\
        .filter(Vacancy.employer_id == current_user.id)\
        .first_or_404()
    
    return render_template('employer/response_detail.html', response=response)

@employer_bp.route('/employer/response/<int:response_id>/update_status', methods=['POST'])
@login_required
def update_response_status(response_id):
    """Обновление статуса отклика"""
    response = VacancyResponse.query\
        .join(Vacancy)\
        .filter(VacancyResponse.id == response_id)\
        .filter(Vacancy.employer_id == current_user.id)\
        .first_or_404()
    
    new_status = request.form.get('status')
    if new_status in ['pending', 'accepted', 'rejected', 'interview']:
        response.status = new_status
        db.session.commit()
        flash('Статус отклика обновлен', 'success')
    else:
        flash('Неверный статус', 'danger')
    
    return redirect(url_for('employer.response_detail', response_id=response_id))

# Поиск кандидатов
@employer_bp.route('/employer/candidates')
@login_required
def search_candidates():
    """Поиск кандидатов"""
    search = request.args.get('search', '')
    industry = request.args.get('industry', '')
    experience = request.args.get('experience', '')
    mbti_type = request.args.get('mbti_type', '')
    sort_by = request.args.get('sort_by', 'relevance')
    
    query = CandidateProfile.query.join(User)
    
    if search:
        query = query.filter(or_(
            CandidateProfile.profession.ilike(f'%{search}%'),
            CandidateProfile.skills.ilike(f'%{search}%'),
            User.fullname.ilike(f'%{search}%')
        ))
    
    if industry and industry != 'all':
        query = query.filter(CandidateProfile.field == industry)
    
    if experience:
        try:
            min_exp = int(experience)
            query = query.filter(CandidateProfile.experience >= min_exp)
        except ValueError:
            pass
    
    if mbti_type and mbti_type != 'all':
        query = query.filter(CandidateProfile.mbti_type == mbti_type)
    
    # Сортировка
    if sort_by == 'experience':
        query = query.order_by(CandidateProfile.experience.desc())
    elif sort_by == 'newest':
        query = query.order_by(User.created_at.desc())
    else:  # relevance
        query = query.order_by(CandidateProfile.experience.desc())
    
    candidates = query.all()
    
    return render_template('employer/candidate_search.html',
                         candidates=candidates,
                         search=search,
                         industry=industry,
                         experience=experience,
                         mbti_type=mbti_type,
                         sort_by=sort_by)

@employer_bp.route('/employer/candidate/<int:candidate_id>')
@login_required
def candidate_detail(candidate_id):
    """Профиль кандидата"""
    candidate = User.query.get_or_404(candidate_id)
    profile = candidate.candidate_profile
    
    if not profile:
        flash('Кандидат не заполнил профиль', 'warning')
        return redirect(url_for('employer.search_candidates'))
    
    # Проверяем, откликался ли кандидат на вакансии компании
    company_responses = VacancyResponse.query\
        .join(Vacancy)\
        .filter(VacancyResponse.candidate_id == candidate_id)\
        .filter(Vacancy.employer_id == current_user.id)\
        .all()
    
    return render_template('employer/candidate_detail.html',
                         candidate=candidate,
                         profile=profile,
                         company_responses=company_responses)

# Настройки и профиль компании
@employer_bp.route('/employer/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Настройки профиля компании"""
    profile = current_user.employer_profile
    if profile is None:
        profile = EmployerProfile(user_id=current_user.id)
        db.session.add(profile)
    
    form = EmployerProfileForm(obj=profile)

    if form.validate_on_submit():
        # Update the profile with form data
        form.populate_obj(profile)
        db.session.commit()
        flash('Настройки успешно сохранены', 'success')
        return redirect(url_for('employer.profile'))
    
    return render_template('employer/settings.html', form=form)

@employer_bp.route('/employer/settings/avatar', methods=['GET', 'POST'])
@login_required
def avatar_settings():
    """Настройки аватара/логотипа компании"""
    form = AvatarForm()
    
    if form.validate_on_submit():
        if form.avatar.data:
            avatar = form.avatar.data.read()
            mimetype = form.avatar.data.mimetype
            current_user.avatar = avatar
            current_user.avatar_mimetype = mimetype
            db.session.commit()
            flash('Логотип компании успешно обновлен', 'success')
        return redirect(url_for('employer.profile'))
    
    return render_template('employer/avatar_settings.html', form=form)

# Аналитика и отчеты
@employer_bp.route('/employer/analytics')
@login_required
def analytics():
    """Аналитика вакансий и откликов"""
    # Статистика по вакансиям
    vacancies = Vacancy.query.filter_by(employer_id=current_user.id).all()
    
    # Статистика по откликам
    responses = VacancyResponse.query\
        .join(Vacancy)\
        .filter(Vacancy.employer_id == current_user.id)\
        .all()
    
    # Статистика по статусам откликов
    status_stats = db.session.query(
        VacancyResponse.status,
        func.count(VacancyResponse.id)
    ).join(Vacancy)\
     .filter(Vacancy.employer_id == current_user.id)\
     .group_by(VacancyResponse.status)\
     .all()
    
    # Статистика по месяцам
    monthly_stats = db.session.query(
        func.date_trunc('month', VacancyResponse.responded_at),
        func.count(VacancyResponse.id)
    ).join(Vacancy)\
     .filter(Vacancy.employer_id == current_user.id)\
     .group_by(func.date_trunc('month', VacancyResponse.responded_at))\
     .order_by(func.date_trunc('month', VacancyResponse.responded_at))\
     .all()
    
    stats = {
        'total_vacancies': len(vacancies),
        'active_vacancies': len([v for v in vacancies if v.is_active]),
        'total_responses': len(responses),
        'status_stats': dict(status_stats),
        'monthly_stats': monthly_stats
    }
    
    return render_template('employer/analytics.html', stats=stats)

# Вспомогательные функции
def check_salary_range(salary_range, title, industry):
    """Проверяет зарплатную вилку на соответствие рыночным данным"""
    market_data = get_market_salary_data()
    
    try:
        # Парсим зарплатную вилку (формат: "100000-150000")
        if '-' in salary_range:
            min_salary = int(salary_range.split('-')[0].strip())
        else:
            min_salary = int(salary_range)
        
        # Определяем категорию по названию должности и отрасли
        category = determine_category(title, industry)
        
        if category in market_data and min_salary < market_data[category]['min']:
            return f"Внимание: предлагаемая зарплата ниже рыночной для данной позиции. Рекомендуемый минимум: {market_data[category]['min']} руб."
            
    except (ValueError, IndexError):
        return "Некорректный формат зарплатной вилки. Используйте формат: '100000-150000'"
    
    return None

def get_market_salary_data():
    """Возвращает рыночные данные по зарплатам"""
    return {
        'developer': {'min': 80000, 'avg': 120000, 'max': 300000},
        'designer': {'min': 60000, 'avg': 90000, 'max': 180000},
        'manager': {'min': 70000, 'avg': 110000, 'max': 250000},
        'analyst': {'min': 65000, 'avg': 95000, 'max': 200000},
        'marketing': {'min': 55000, 'avg': 85000, 'max': 160000},
        'it': {'min': 70000, 'avg': 100000, 'max': 220000},
        'finance': {'min': 65000, 'avg': 95000, 'max': 200000},
        'education': {'min': 40000, 'avg': 60000, 'max': 120000}
    }

def determine_category(title, industry):
    """Определяет категорию вакансии"""
    title_lower = title.lower()
    
    if any(word in title_lower for word in ['разработчик', 'developer', 'программист', 'инженер']):
        return 'developer'
    elif any(word in title_lower for word in ['дизайнер', 'designer']):
        return 'designer'
    elif any(word in title_lower for word in ['менеджер', 'manager', 'руководитель']):
        return 'manager'
    elif any(word in title_lower for word in ['аналитик', 'analyst']):
        return 'analyst'
    elif any(word in title_lower for word in ['маркетолог', 'marketing']):
        return 'marketing'
    else:
        # Если категорию не определили, используем отрасль
        return industry.lower()

def get_recommended_vacancies(employer_profile):
    """Получить вакансии, подходящие под профиль работодателя"""
    if not employer_profile:
        return []
    
    # Получаем все активные вакансии, кроме созданных текущим работодателем
    all_vacancies = Vacancy.query.filter(
        Vacancy.is_active == True,
        Vacancy.employer_id != current_user.id
    ).all()
    
    recommended = []
    
    for vacancy in all_vacancies:
        score = calculate_match_score(employer_profile, vacancy)
        if score > 0.3:  # Порог совпадения 30%
            recommended.append((vacancy, score))
    
    # Сортируем по убыванию релевантности
    recommended.sort(key=lambda x: x[1], reverse=True)
    
    return [vacancy for vacancy, score in recommended[:5]]

def calculate_match_score(employer_profile, vacancy):
    """Рассчитать степень совпадения профиля работодателя с вакансией"""
    score = 0
    max_score = 0
    
    # Совпадение по индустрии
    if employer_profile.industry and vacancy.industry:
        max_score += 1
        if employer_profile.industry.lower() == vacancy.industry.lower():
            score += 1
    
    # Совпадение по предпочтительным MBTI типам
    if employer_profile.preferred_mbti and vacancy.required_mbti:
        max_score += 1
        employer_mbti = [mbti.strip().upper() for mbti in employer_profile.preferred_mbti.split(',')]
        vacancy_mbti = [mbti.strip().upper() for mbti in vacancy.required_mbti.split(',')]
        
        common_mbti = set(employer_mbti) & set(vacancy_mbti)
        if common_mbti:
            score += len(common_mbti) / len(employer_mbti)
    
    # Учитываем размер команды работодателя
    if employer_profile.team_size:
        max_score += 0.5
        # Даем базовый балл если размер команды указан
        score += 0.5
    
    return score / max_score if max_score > 0 else 0

def calculate_employer_completion(profile):
    """Рассчитать процент заполненности профиля работодателя"""
    if not profile:
        return 0
        
    fields = [
        profile.company_name,
        profile.industry,
        profile.team_size,
        profile.preferred_mbti,
        profile.company_description
    ]
    
    filled = sum(1 for field in fields if field)
    return int((filled / len(fields)) * 100) if fields else 0