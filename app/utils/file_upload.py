import os
from werkzeug.utils import secure_filename
from flask import current_app
from datetime import datetime

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}
ALLOWED_DOC_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename, file_type='video'):
    extensions = ALLOWED_VIDEO_EXTENSIONS if file_type == 'video' else ALLOWED_DOC_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in extensions

def upload_video(file):
    if not allowed_file(file.filename):
        raise ValueError('Недопустимый формат видео')
    
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"video_{timestamp}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_folder, filename)
    
    file.save(filepath)
    return os.path.join('uploads', 'videos', filename)

def upload_document(file):
    if not allowed_file(file.filename, 'doc'):
        raise ValueError('Недопустимый формат документа')
    
    upload_folder = current_app.config['DOCUMENT_FOLDER']
    os.makedirs(upload_folder, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"doc_{timestamp}_{secure_filename(file.filename)}"
    filepath = os.path.join(upload_folder, filename)
    
    file.save(filepath)
    return os.path.join('uploads', 'documents', filename)