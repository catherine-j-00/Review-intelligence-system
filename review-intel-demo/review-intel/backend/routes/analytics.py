from flask import Blueprint, jsonify, request
from ..analytics import queries as q
from ..database.models import ReviewAnalysis
from .auth_utils import require_auth

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
bp.before_request(require_auth)


@bp.errorhandler(ValueError)
def bad_input(exc):
    return jsonify(error='Invalid filter value: ' + str(exc)), 400


@bp.get('/overview')
def overview():
    return jsonify(q.overview(request.args))


@bp.get('/products')
def products():
    return jsonify(q.product_rankings(request.args, limit=int(request.args.get('limit', 5))))


@bp.get('/products/<int:product_id>')
def product_detail(product_id):
    detail = q.product_detail(product_id, request.args)
    if detail is None:
        return jsonify(error='Product not found'), 404
    return jsonify(detail)


@bp.get('/brands')
def brands():
    return jsonify(q.brand_stats(request.args))


@bp.get('/monthly')
def monthly():
    return jsonify(q.monthly(request.args))


@bp.get('/seasonal')
def seasonal():
    return jsonify(q.seasonal(request.args))


@bp.get('/emotions')
def emotions():
    return jsonify(q.distribution(ReviewAnalysis.emotion, request.args))


@bp.get('/sentiments')
def sentiments():
    return jsonify(q.distribution(ReviewAnalysis.sentiment, request.args))
