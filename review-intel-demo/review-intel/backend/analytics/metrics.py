from sqlalchemy import case, func
from ..database.models import Review, ReviewAnalysis


def pct(part, total):
    '''part / total x 100, safe when total is 0.'''
    return round(part * 100.0 / total, 1) if total else 0.0


def count_if(condition):
    return func.coalesce(func.sum(case((condition, 1), else_=0)), 0)


def sentiment_columns():
    '''total, positive, negative, neutral. Always in this order.'''
    return [func.count(Review.review_id),
            count_if(ReviewAnalysis.sentiment == 'positive'),
            count_if(ReviewAnalysis.sentiment == 'negative'),
            count_if(ReviewAnalysis.sentiment == 'neutral')]


def sentiment_block(total, pos, neg, neu):
    total, pos, neg, neu = int(total), int(pos), int(neg), int(neu)
    return {'total_reviews': total, 'positive': pos, 'negative': neg, 'neutral': neu,
            'positive_pct': pct(pos, total), 'negative_pct': pct(neg, total),
            'neutral_pct': pct(neu, total)}
