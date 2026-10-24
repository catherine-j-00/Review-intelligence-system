import pandas as pd
from flask import Blueprint, jsonify, request
from ..analytics.filters import apply_filters, base_query
from ..database.db import db
from ..database.models import Review
from ..services.review_service import save_review, import_dataframe
from ..services.serializers import serialize_review
from .auth_utils import require_auth

bp = Blueprint('reviews', __name__, url_prefix='/api/reviews')
bp.before_request(require_auth)


@bp.post('')
def create_review():
    data = request.get_json(silent=True) or {}
    try:
        review = save_review(data, default_date_today=True)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    if review is None:
        return jsonify(error='A review with this review_id already exists'), 409
    db.session.commit()
    return jsonify(serialize_review(review)), 201


@bp.post('/bulk')
def bulk_upload():
    file = request.files.get('file')
    if not file or not file.filename.lower().endswith('.csv'):
        return jsonify(error='Upload a .csv file in the form field named file'), 400
    is_sample = request.form.get('is_sample', 'false').lower() == 'true'
    try:
        df = pd.read_csv(file, dtype=str, encoding='utf-8-sig').fillna('')
        summary = import_dataframe(df, is_sample=is_sample)
    except (ValueError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        return jsonify(error=str(exc)), 400
    return jsonify(summary)


@bp.get('')
def list_reviews():
    page = max(int(request.args.get('page', 1)), 1)
    per_page = min(int(request.args.get('per_page', 25)), 100)
    query = apply_filters(base_query(Review), request.args)
    total = query.count()
    rows = (query.order_by(Review.review_date.desc(), Review.review_id.desc())
            .offset((page - 1) * per_page).limit(per_page).all())
    return jsonify(total=total, page=page, per_page=per_page,
                   items=[serialize_review(r) for r in rows])
