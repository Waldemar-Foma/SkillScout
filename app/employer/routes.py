from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.employer import EmployerProfile, Vacancy
from app.employer.forms import EmployerProfileForm, VacancyForm

employer_bp = Blueprint('employer', __name__)

@employer_bp.route('/dashboard')
@login_required
def dashboard():
    profile = current_user.employer_profile
    vacancies = Vacancy.query.filter_by(employer_id=profile.id).all()
    return render_template('employer/dashboard.html', 
                         profile=profile,
                         vacancies=vacancies)


@employer_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = EmployerProfileForm()
    profile = current_user.employer_profile or EmployerProfile(user=current_user)
    
    if form.validate_on_submit():
        profile.company_name = form.company_name.data
        profile.company_description = form.company_description.data
        profile.industry = form.industry.data
        profile.website = form.website.data
        profile.team_size = form.team_size.data
        
        db.session.add(profile)
        db.session.commit()
        flash('Профиль компании обновлен', 'success')
        return redirect(url_for('employer.dashboard'))
    
    elif request.method == 'GET':
        form.company_name.data = profile.company_name
        form.company_description.data = profile.company_description
        form.industry.data = profile.industry
        form.website.data = profile.website
        form.team_size.data = profile.team_size
    
    return render_template('employer/profile.html', form=form)

@employer_bp.route('/vacancy/new', methods=['GET', 'POST'])
@login_required
def new_vacancy():
    form = VacancyForm()
    if form.validate_on_submit():
        vacancy = Vacancy(
            employer_id=current_user.employer_profile.id,
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            location=form.location.data,
            salary_range=form.salary_range.data,
            is_remote=form.is_remote.data,
            required_mbti=form.required_mbti.data
        )
        db.session.add(vacancy)
        db.session.commit()
        flash('Вакансия создана', 'success')
        return redirect(url_for('employer.dashboard'))
    
    return render_template('employer/vacancy_form.html', form=form)