import os
import cv2
import numpy as np
from datetime import datetime

def save_video_profile(video_file, user_id):
    """
    Сохраняет видео файл и возвращает путь к нему
    """
    try:
        # Создаем папку для видео если не существует
        upload_folder = os.path.join('app', 'static', 'uploads', 'videos')
        os.makedirs(upload_folder, exist_ok=True)
        
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"video_{user_id}_{timestamp}.mp4"
        filepath = os.path.join(upload_folder, filename)
        
        # Сохраняем файл
        video_file.save(filepath)
        
        return {
            'filename': filename,
            'filepath': filepath,
            'success': True
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def analyze_video_content(video_path):
    """
    Анализирует видео контент (заглушка для демонстрации)
    В реальном приложении здесь будет анализ эмоций, речи и т.д.
    """
    try:
        # Заглушка для демонстрации
        analysis_results = {
            'emotions': {
                'confidence': 0.85,
                'energy': 0.72,
                'clarity': 0.78
            },
            'speech_analysis': {
                'pace': 'moderate',
                'clarity': 'good',
                'volume': 'appropriate'
            },
            'overall_score': 82,
            'recommendations': [
                "Хороший уровень уверенности",
                "Рекомендуется больше жестикулировать",
                "Темп речи оптимальный"
            ]
        }
        
        return analysis_results
    except Exception as e:
        return {
            'error': str(e),
            'overall_score': 0
        }

def extract_video_metadata(video_path):
    """
    Извлекает базовые метаданные видео
    """
    try:
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
            
        # Получаем базовую информацию о видео
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            'duration': duration,
            'fps': fps,
            'frame_count': frame_count
        }
    except Exception as e:
        return {
            'error': str(e)
        }