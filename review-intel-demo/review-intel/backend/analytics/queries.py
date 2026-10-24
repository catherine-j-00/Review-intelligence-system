from sqlalchemy import extract, func
from ..config import Config
from ..database.db import db
from ..database.models import Brand, Category, Product, Review, ReviewAnalysis
from ..services.serializers import serialize_review
from .filters import apply_filters, as_dict, base_query
from .metrics import pct, sentiment_block, sentiment_columns


def overview(args):
    q = base_query(*sentiment_columns(),
                   func.count(func.distinct(Review.product_id)),
                   func.count(func.distinct(Product.brand_id)))
    total, pos, neg, neu, products, brands = apply_filters(q, args).one()
    out = sentiment_block(total, pos, neg, neu)
    out.update(products=products, brands=brands, note='Counts are reviews, not sales.')
    return out


def product_stats(args):
    group = (Product.product_id, Product.product_name, Brand.brand_name, Category.category_name)
    q = (base_query(*group, *sentiment_columns())
         .filter(Review.product_id.isnot(None)).group_by(*group))
    return [dict(product_id=r[0], product=r[1], brand=r[2], category=r[3],
                 **sentiment_block(r[4], r[5], r[6], r[7]))
            for r in apply_filters(q, args).all()]


def product_rankings(args, limit=5):
    stats = product_stats(args)
    # A product with 3 reviews should not beat one with 300 on percentages, so
    # percentage rankings only include products above a minimum review count.
    eligible = [s for s in stats if s['total_reviews'] >= Config.MIN_REVIEWS_FOR_RANKING]
    return {
        'min_reviews_for_ranking': Config.MIN_REVIEWS_FOR_RANKING,
        'most_reviewed': sorted(stats, key=lambda s: -s['total_reviews'])[:limit],
        'most_positive_reviews': sorted(stats, key=lambda s: -s['positive'])[:limit],
        'most_negative_reviews': sorted(stats, key=lambda s: -s['negative'])[:limit],
        'highest_positive_pct': sorted(eligible, key=lambda s: (-s['positive_pct'], -s['total_reviews']))[:limit],
        'highest_negative_pct': sorted(eligible, key=lambda s: (-s['negative_pct'], -s['total_reviews']))[:limit],
    }


def brand_stats(args):
    q = (base_query(Brand.brand_name, *sentiment_columns())
         .filter(Brand.brand_id.isnot(None)).group_by(Brand.brand_name))
    rows = apply_filters(q, args).all()
    eq = (base_query(Brand.brand_name, ReviewAnalysis.emotion, func.count(Review.review_id))
          .filter(Brand.brand_id.isnot(None)).group_by(Brand.brand_name, ReviewAnalysis.emotion))
    emotions = {}
    for brand, emotion, n in apply_filters(eq, args).all():
        emotions.setdefault(brand, {})[emotion] = n
    out = [dict(brand=r[0], emotions=emotions.get(r[0], {}),
                **sentiment_block(r[1], r[2], r[3], r[4])) for r in rows]
    return sorted(out, key=lambda b: -b['total_reviews'])


def distribution(column, args):
    '''Used for both /emotions and /sentiments.'''
    q = base_query(column, func.count(Review.review_id)).group_by(column)
    rows = apply_filters(q, args).all()
    total = sum(n for _, n in rows)
    return [{'label': label, 'count': n, 'pct': pct(n, total)}
            for label, n in sorted(rows, key=lambda r: -r[1])]


def monthly(args):
    year = extract('year', Review.review_date).label('y')
    month = extract('month', Review.review_date).label('m')
    q = base_query(year, month, *sentiment_columns()).group_by(year, month).order_by(year, month)
    rows = apply_filters(q, args).all()
    eq = (base_query(year, month, ReviewAnalysis.emotion, func.count(Review.review_id))
          .group_by(year, month, ReviewAnalysis.emotion))
    emotions = {}
    for y, m, emotion, n in apply_filters(eq, args).all():
        emotions.setdefault((int(y), int(m)), {})[emotion] = n
    return [dict(month='%04d-%02d' % (int(r[0]), int(r[1])),
                 emotions=emotions.get((int(r[0]), int(r[1])), {}),
                 **sentiment_block(r[2], r[3], r[4], r[5])) for r in rows]


def season_of(month):
    for name, months in Config.SEASON_MONTHS.items():
        if month in months:
            return name
    return 'Other'


def seasonal(args):
    month = extract('month', Review.review_date).label('m')
    q = (base_query(month, Category.category_name, *sentiment_columns())
         .group_by(month, Category.category_name))
    buckets = {}
    for m, category, total, pos, neg, neu in apply_filters(q, args).all():
        key = (season_of(int(m)), category or 'Uncategorised')
        b = buckets.setdefault(key, [0, 0, 0, 0])
        for i, value in enumerate((total, pos, neg, neu)):
            b[i] += int(value)
    rows = [dict(season=s, category=c, **sentiment_block(*v)) for (s, c), v in buckets.items()]
    history = len(monthly({'data': args.get('data', 'real')}))
    return {'basis': 'Review activity and feedback trends. NOT sales.',
            'months_of_history': history,
            'enough_history': history >= 12,  # seasons need at least a year of data
            'season_months': Config.SEASON_MONTHS,
            'rows': sorted(rows, key=lambda r: (r['season'], -r['total_reviews']))}


# ---- Common complaints / praise: transparent keyword matching ----
ASPECTS = {
    'durability': ['last', 'lasts', 'lasting', 'durable', 'fade', 'faded', 'smudge', 'wear', 'broke', 'broken'],
    'colour/shade': ['colour', 'color', 'shade', 'tone', 'pigment'],
    'packaging': ['packaging', 'package', 'box', 'bottle', 'cap', 'seal'],
    'price': ['price', 'expensive', 'costly', 'value'],
    'smell': ['smell', 'scent', 'fragrance'],
    'texture': ['texture', 'sticky', 'creamy', 'dry', 'greasy'],
    'delivery': ['delivery', 'shipping', 'late', 'delayed'],
    'quality': ['quality', 'cheap', 'fake'],
}


def top_aspects(args, sentiment, limit=5):
    scope = as_dict(args)
    scope['sentiment'] = sentiment
    # Filters must be applied BEFORE limit(): SQLAlchemy refuses filter() after limit().
    q = apply_filters(base_query(Review.review_text), scope)
    q = q.order_by(Review.review_date.desc()).limit(5000)
    counts = {}
    for (text,) in q.all():
        words = set(w.strip('.,!?;:()').lower() for w in text.split())
        for aspect, keys in ASPECTS.items():
            if words & set(keys):
                counts[aspect] = counts.get(aspect, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: -kv[1])[:limit]
    return [{'aspect': a, 'mentions': n} for a, n in ranked]


def recent_reviews(args, limit=10, sentiment=None):
    scope = as_dict(args)
    if sentiment:
        scope['sentiment'] = sentiment
    q = apply_filters(base_query(Review), scope)
    rows = q.order_by(Review.review_date.desc(), Review.review_id.desc()).limit(limit).all()
    return [serialize_review(r) for r in rows]


def product_detail(product_id, args):
    product = db.session.get(Product, product_id)
    if product is None:
        return None
    scope = as_dict(args)
    scope['product_id'] = product_id
    return {
        'product': product.product_name,
        'brand': product.brand.brand_name if product.brand else None,
        'category': product.category.category_name if product.category else None,
        'summary': overview(scope),
        'emotions': distribution(ReviewAnalysis.emotion, scope),
        'monthly': monthly(scope),
        'recent_reviews': recent_reviews(scope),
        'common_complaints': top_aspects(scope, 'negative'),
        'common_positive_feedback': top_aspects(scope, 'positive'),
        'note': 'Complaints and praise are keyword matches inside negative/positive reviews.',
    }
