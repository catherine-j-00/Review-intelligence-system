# ADAPT: use the exact emotion labels your model outputs (lowercase).
EMOTION_TO_SENTIMENT = {
    'joy': 'positive', 'love': 'positive', 'happiness': 'positive',
    'admiration': 'positive', 'satisfaction': 'positive',
    'anger': 'negative', 'sadness': 'negative', 'fear': 'negative',
    'disgust': 'negative', 'disappointment': 'negative', 'annoyance': 'negative',
    'surprise': 'neutral', 'neutral': 'neutral',
}


def emotion_to_sentiment(emotion):
    # Unknown labels become neutral rather than crashing.
    return EMOTION_TO_SENTIMENT.get((emotion or '').lower().strip(), 'neutral')
