from datetime import date
from sqlalchemy import extract, func
from ..database.db import db
from ..database.models import Brand, Category, Product, Review, ReviewAnalysis


def as_dict(args):
    return args.to_dict() if hasattr(args, 'to_dict') else dict(args)


def base_query(*columns):
    return (db.session.query(*columns)
            .select_from(Review)
            .join(ReviewAnalysis, ReviewAnalysis.review_id == Review.review_id)
            .outerjoin(Product, Product.product_id == Review.product_id)
            .outerjoin(Brand, Brand.brand_id == Product.brand_id)
            .outerjoin(Category, Category.category_id == Product.category_id))


def apply_filters(query, args):
    '''args can be request.args or a normal dict. Text matches ignore upper/lower case.'''
    def get(key):
        value = args.get(key)
        if value is None:
            return None
        value = str(value).strip()
        return value or None

    if get('product_id'):
        query = query.filter(Product.product_id == int(get('product_id')))
    if get('product'):
        query = query.filter(func.lower(Product.product_name) == get('product').lower())
    if get('brand'):
        query = query.filter(func.lower(Brand.brand_name) == get('brand').lower())
    if get('category'):
        query = query.filter(func.lower(Category.category_name) == get('category').lower())
    if get('sentiment'):
        query = query.filter(ReviewAnalysis.sentiment == get('sentiment').lower())
    if get('emotion'):
        query = query.filter(ReviewAnalysis.emotion == get('emotion').lower())
    if get('date_from'):
        query = query.filter(Review.review_date >= date.fromisoformat(get('date_from')))
    if get('date_to'):
        query = query.filter(Review.review_date <= date.fromisoformat(get('date_to')))
    if get('year'):
        query = query.filter(extract('year', Review.review_date) == int(get('year')))
    if get('month'):
        query = query.filter(extract('month', Review.review_date) == int(get('month')))

    # Sample data is hidden unless you ask for it: data=real (default) | sample | all
    data = (get('data') or 'real').lower()
    if data == 'real':
        query = query.filter(Review.is_sample.is_(False))
    elif data == 'sample':
        query = query.filter(Review.is_sample.is_(True))
    return query
