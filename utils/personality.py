from transformers import pipeline
import numpy as np


def analyze_personality(text):
    """
    Анализирует текст и возвращает OCEAN-характеристики личности
    Возвращает словарь с показателями от 0 до 1:
    {
        'openness': 0.7,
        'conscientiousness': 0.6,
        'extraversion': 0.5,
        'agreeableness': 0.8,
        'neuroticism': 0.3
    }
    """
    # Загружаем модель для анализа тональности (в реальном проекте используйте OCEAN-специфичную модель)
    classifier = pipeline("text-classification", model="cointegrated/rubert-tiny")

    # Временная заглушка - в реальном проекте замените на настоящий анализ OCEAN
    # Здесь мы просто генерируем случайные значения для демонстрации
    ocean_scores = {
        'openness': round(np.random.uniform(0.3, 0.9), 2),
        'conscientiousness': round(np.random.uniform(0.2, 0.8), 2),
        'extraversion': round(np.random.uniform(0.4, 0.7), 2),
        'agreeableness': round(np.random.uniform(0.5, 0.9), 2),
        'neuroticism': round(np.random.uniform(0.1, 0.6), 2)
    }

    return ocean_scores


def ocean_to_mbti(ocean_scores):
    """
    Конвертирует OCEAN-показатели в тип MBTI
    """
    # E/I (экстраверсия/интроверсия)
    ei = 'E' if ocean_scores['extraversion'] > 0.5 else 'I'

    # N/S (интуиция/сенсорика) - на основе открытости опыту
    ns = 'N' if ocean_scores['openness'] > 0.6 else 'S'

    # T/F (мышление/чувствование) - на основе доброжелательности
    tf = 'F' if ocean_scores['agreeableness'] > 0.55 else 'T'

    # J/P (суждение/восприятие) - на основе добросовестности
    jp = 'J' if ocean_scores['conscientiousness'] > 0.5 else 'P'

    return f"{ei}{ns}{tf}{jp}"
