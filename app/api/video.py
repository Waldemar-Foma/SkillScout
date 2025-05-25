from flask import Blueprint, request, jsonify
from flask_login import current_user, login_required
from app.utils.video_processing import save_video_profile
from app.utils.ai_analysis import VideoAnalyzer
from app.models.candidate import CandidateVideo
from app.extensions import db

video_bp = Blueprint('video', __name__)
video_analyzer = VideoAnalyzer()

@video_bp.route('/upload', methods=['POST'])
@login_required
def upload_video():
    if 'video' not in request.files:
        return jsonify({'error': 'No video file provided'}), 400
    
    video_file = request.files['video']
    result = save_video_profile(current_user.id, video_file)
    
    if result.get('status') == 'error':
        return jsonify(result), 400
    
    # Анализ видео (можно вынести в фоновую задачу)
    analysis = video_analyzer.full_analysis(result['filepath'], current_user.id)
    return jsonify({
        'status': 'success',
        'filename': result['filename'],
        'analysis': analysis
    }), 200

@video_bp.route('/analyze/<int:video_id>')
@login_required
def get_analysis(video_id):
    video = CandidateVideo.query.filter_by(
        id=video_id,
        user_id=current_user.id
    ).first_or_404()
    
    if not video.analysis:
        analysis = video_analyzer.full_analysis(video.filepath, current_user.id)
        return jsonify(analysis), 200
    
    return jsonify(video.analysis), 200