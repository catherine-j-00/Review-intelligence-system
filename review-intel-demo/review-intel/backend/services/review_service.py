from datetime import date
import pandas as pd
from sqlalchemy import func
from ..config import Config
from ..database.db import db
from ..database.models import Brand, Category, Product, Review, ReviewAnalysis
from .analysis_service import analyze_text


def _clean(value):
    return ' '.join(str(value).split()) if value is not None else ''


def _get_or_create(model, column_name, name):
    '''Case-insensitive: Lakme, LAKME and lakme become one brand.'''
    column = getattr(model, column_name)
    obj = model.query.filter(func.lower(column) == name.lower()).first()
    if obj is None:
        obj = model(**{column_name: name})
        db.session.add(obj)
        db.session.flush()
    return obj


def _get_or_create_product(name, brand, category):
    brand_id = brand.brand_id if brand else None
    product = Product.query.filter(func.lower(Product.product_name) == name.lower(),
                                   Product.brand_id == brand_id).first()
    if product is None:
        product = Product(product_name=name, brand_id=brand_id,
                          category_id=category.category_id if category else None)
        db.session.add(product)
        db.session.flush()
    return product


def parse_date(value):
    if value in (None, ''):
        return None
    parsed = pd.to_datetime(value, errors='coerce')
    if pd.isna(parsed):
        raise ValueError('Invalid date: ' + str(value) + ' (use YYYY-MM-DD)')
    return parsed.date()


def save_review(row, is_sample=False, default_date_today=False):
    '''Validate, analyze and store ONE review. Returns the Review, or None if duplicate.'''
    text = _clean(row.get('review_text'))
    if not text:
        raise ValueError('review_text is empty')
    if len(text) > 5000:
        raise ValueError('review_text is longer than 5000 characters')

    external_id = _clean(row.get('review_id')) or None
    if external_id and Review.query.filter_by(external_id=external_id).first():
        return None

    review_date = parse_date(row.get('review_date'))
    if review_date is None:
        if default_date_today:  # only used for manual single reviews
            review_date = date.today()
        else:
            raise ValueError('review_date is missing')

    product = None
    product_name = _clean(row.get('product_name'))
    if product_name:
        brand_name = _clean(row.get('brand'))
        category_name = _clean(row.get('category'))
        brand = _get_or_create(Brand, 'brand_name', brand_name) if brand_name else None
        category = _get_or_create(Category, 'category_name', category_name) if category_name else None
        product = _get_or_create_product(product_name, brand, category)

    result = analyze_text(text)
    confidence = result['confidence']
    review = Review(external_id=external_id, review_text=text, review_date=review_date,
                    product_id=product.product_id if product else None, is_sample=is_sample)
    review.analysis = ReviewAnalysis(
        sentiment=result['sentiment'], emotion=result['emotion'],
        confidence_score=confidence,
        needs_review=(confidence is not None and confidence < Config.CONFIDENCE_THRESHOLD),
        model_version=Config.MODEL_VERSION)
    db.session.add(review)
    db.session.flush()
    return review


def import_dataframe(df, is_sample=False):
    missing = [c for c in ('review_text', 'review_date') if c not in df.columns]
    if missing:
        raise ValueError('CSV is missing columns: ' + ', '.join(missing))
    summary = {'inserted': 0, 'skipped_duplicates': 0, 'errors': []}
    for line_no, row in enumerate(df.to_dict('records'), start=2):  # line 1 is the header
        try:
            with db.session.begin_nested():  # a bad row rolls back only itself
                review = save_review(row, is_sample=is_sample)
                if review is None:
                    summary['skipped_duplicates'] += 1
                else:
                    summary['inserted'] += 1
        except Exception as exc:
            summary['errors'].append({'row': line_no, 'error': str(exc)})
        if line_no % 100 == 0:
            db.session.commit()
    db.session.commit()
    return summary
