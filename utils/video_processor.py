import os
import speech_recognition as sr
from moviepy.editor import VideoFileClip

def process_video(video_path):
    """Извлекает аудио из видео и преобразует его в текст"""
    try:
        # Извлечение аудио
        audio_path = "temp_audio.wav"
        video = VideoFileClip(video_path)
        video.audio.write_audiofile(audio_path)
        video.close()
        
        # Преобразование аудио в текст
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="ru-RU")
        
        # Удаление временного файла
        os.remove(audio_path)
        
        return text
    
    except Exception as e:
        print(f"Ошибка обработки видео: {str(e)}")
        raise