from ml_model.predictor import predict
from .sentiment_mapper import emotion_to_sentiment


def analyze_text(text):
    result = predict(text)
    return {
        'sentiment': emotion_to_sentiment(result['emotion']),
        'emotion': result['emotion'],
        'confidence': result['confidence'],
    }
