from flask_login import login_required, current_user
from app.candidate.forms import CandidateProfileForm
from app.models.candidate import CandidateProfile, CandidateVideo
from app.utils.video_processing import save_video_profile, analyze_video_content
from app import db
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
import os

candidate_bp = Blueprint('candidate', __name__)

@candidate_bp.route('/dashboard')
@login_required
def dashboard():
    profile = current_user.candidate_profile
    videos = CandidateVideo.query.filter_by(user_id=current_user.id).all()
    return render_template('candidate/dashboard.html', 
                         profile=profile,
                         videos=videos,
                         profile_completion=calculate_completion(profile))

@candidate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = CandidateProfileForm()
    profile = current_user.candidate_profile or CandidateProfile(user=current_user)
    
    if form.validate_on_submit():
        profile.profession = form.profession.data
        profile.experience = form.experience.data
        profile.skills = form.skills.data
        profile.mbti_type = form.mbti_type.data
        
        if form.video_resume.data:
            video_url = save_video_profile(current_user.id, form.video_resume.data)
            profile.video_resume = video_url
        
        db.session.add(profile)
        db.session.commit()
        flash('Профиль успешно обновлен', 'success')
        return redirect(url_for('candidate.dashboard'))
    
    elif request.method == 'GET':
        form.profession.data = profile.profession
        form.experience.data = profile.experience
        form.skills.data = profile.skills
        form.mbti_type.data = profile.mbti_type
    
    return render_template('candidate/profile.html', form=form)

@candidate_bp.route('/video/analyze/<int:video_id>')
@login_required
def analyze_video(video_id):
    video = CandidateVideo.query.filter_by(id=video_id, user_id=current_user.id).first_or_404()
    analysis = analyze_video_content(video.filepath)
    video.analysis = analysis
    db.session.commit()
    return jsonify(analysis)

def calculate_completion(profile):
    if not profile:
        return 0
        
    fields = [
        profile.profession,
        profile.experience is not None,
        profile.skills,
        profile.mbti_type,
        profile.video_resume
    ]
    
    filled = sum(1 for field in fields if field)
    return int((filled / len(fields)) * 100)