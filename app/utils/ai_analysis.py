import os
import cv2
import librosa
import subprocess
from flask import current_app
from werkzeug.utils import secure_filename
from deepface import DeepFace
from app.extensions import db
from app.models.candidate import CandidateVideo
from transformers import pipeline


class VideoAnalyzer:
    def __init__(self):
        self.speech_analyzer = pipeline("text-classification", model="finiteautomata/bertweet-base-sentiment-analysis")

    def allowed_video(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_VIDEO_EXTENSIONS']

    def save_video_profile(self, user_id, video_file):
        if not self.allowed_video(video_file.filename):
            return None

        upload_folder = current_app.config['VIDEO_UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)

        filename = secure_filename(f"{user_id}_{video_file.filename}")
        filepath = os.path.join(upload_folder, filename)
        video_file.save(filepath)

        video = CandidateVideo(
            user_id=user_id,
            filename=filename,
            filepath=filepath
        )
        db.session.add(video)
        db.session.commit()

        return filepath

    def analyze_video_content(self, video_path):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            current_app.logger.error(f"Cannot open video: {video_path}")
            return None

        emotions = []

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if int(cap.get(cv2.CAP_PROP_POS_FRAMES)) % 10 == 0:
                try:
                    analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
                    if isinstance(analysis, list):
                        emotions.append(analysis[0]['dominant_emotion'])
                    else:
                        emotions.append(analysis['dominant_emotion'])
                except Exception as e:
                    current_app.logger.error(f"Emotion analysis error: {e}")

        cap.release()

        audio_path = os.path.join(current_app.config['VIDEO_UPLOAD_FOLDER'], 'temp_audio.mp3')
        try:
            subprocess.run([
                "ffmpeg", "-y", "-i", video_path, "-q:a", "0", "-map", "a", audio_path
            ], check=True)
            y, sr = librosa.load(audio_path)
            os.remove(audio_path)
        except Exception as e:
            current_app.logger.error(f"Audio extraction or processing error: {e}")
            y, sr = None, None

        speech_rate = 0
        if y is not None and sr is not None:
            speech_rate = len(librosa.effects.split(y, top_db=30)) / (len(y)/sr) * 60

        return {
            'emotions': max(set(emotions), key=emotions.count) if emotions else 'neutral',
            'speech_rate': speech_rate,
        }
