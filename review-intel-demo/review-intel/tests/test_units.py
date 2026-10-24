from backend.analytics.metrics import pct
from backend.services.sentiment_mapper import emotion_to_sentiment


def test_pct():
    assert pct(1, 4) == 25.0
    assert pct(0, 0) == 0.0  # no division by zero


def test_mapper():
    assert emotion_to_sentiment('Joy') == 'positive'
    assert emotion_to_sentiment('anger') == 'negative'
    assert emotion_to_sentiment('something-new') == 'neutral'
