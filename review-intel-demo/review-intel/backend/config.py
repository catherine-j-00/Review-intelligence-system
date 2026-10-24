import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only')
    JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']  # app refuses to start without it
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    FRONTEND_ORIGIN = os.environ.get('FRONTEND_ORIGIN', 'http://localhost:5173')
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
    CHATBOT_MODEL = os.environ.get('CHATBOT_MODEL', 'claude-sonnet-5-5')
    MIN_REVIEWS_FOR_RANKING = int(os.environ.get('MIN_REVIEWS_FOR_RANKING', 20))
    CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', 0.5))
    MODEL_VERSION = os.environ.get('MODEL_VERSION', 'emotion-v1')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # reject uploads over 5 MB
    SHOPMOOD_API_KEY = os.getenv("SHOPMOOD_API_KEY", "")
    # Seasons are regional. Edit this for your market. Month numbers 1-12.
    SEASON_MONTHS = {
        'Summer': [3, 4, 5],
        'Monsoon': [6, 7, 8],
        'Festival season': [9, 10, 11],
        'Winter': [12, 1, 2],
    }
