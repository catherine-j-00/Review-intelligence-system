import html


def clean_text(text):
    '''Light cleaning only. If your model already has its own vectorizer inside
    the pickle, do NOT repeat its steps here.'''
    text = html.unescape(text or '')
    words = [w for w in text.split() if not w.startswith('http')]
    return ' '.join(words)
