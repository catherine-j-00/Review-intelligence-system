
import hmac

from flask import Blueprint, current_app, jsonify, request

from ..database.db import db
from ..services.review_service import save_review
from ..services.serializers import serialize_review
from ..database.models import Brand

bp = Blueprint(
    "customer_reviews",
    __name__,
    url_prefix="/api/customer/reviews",
)


def valid_shopmood_request():
    expected = current_app.config.get("SHOPMOOD_API_KEY", "")
    supplied = request.headers.get("X-ShopMood-Key", "")

    return bool(expected) and hmac.compare_digest(expected, supplied)


@bp.post("")
def submit_customer_review():
    # Only ShopMood's server should call this endpoint.
    if not valid_shopmood_request():
        return jsonify(error="Unauthorized"), 401

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify(error="A JSON object is required"), 400

    # Accept only the fields needed for review processing.
    row = {
    "review_text": data.get("review_text"),
    "product_name": data.get("product_name"),
    "brand": data.get("brand"),
    "category": data.get("category"),
    "review_date": data.get("review_date"),
     }

    try:
        review = save_review(row, default_date_today=True)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify(error=str(exc)), 400
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Customer review submission failed")
        return jsonify(error="Could not save review"), 500

    return jsonify({
    "review_id": review.review_id,
    "review_text": review.review_text,
    "product_name": (
        review.product.product_name if review.product else None
    ),
    "review_date": (
        review.review_date.isoformat()
        if review.review_date else None
    ),
    "sentiment": review.analysis.sentiment if review.analysis else None,
    "emotion": review.analysis.emotion if review.analysis else None,
    "confidence": (
        review.analysis.confidence_score
        if review.analysis else None
    ),
}), 201


@bp.get("")
def get_customer_reviews():
    if not valid_shopmood_request():
        return jsonify(error="Unauthorized"), 401

    product_name = request.args.get("product_name", "").strip()
    brand_name = request.args.get("brand", "").strip()

    if not product_name:
        return jsonify(error="product_name is required"), 400

    try:
        limit = int(request.args.get("limit", 5))
        offset = int(request.args.get("offset", 0))

        # Normal requests can load 5; Show all can request up to 1000.
        if not 1 <= limit <= 1000 or offset < 0:
            raise ValueError
    except (TypeError, ValueError):
        return jsonify(error="Invalid limit or offset"), 400

    try:
        from ..database.models import Product, Review, Brand

        query = Product.query.filter_by(product_name=product_name)

        if brand_name:
            query = query.join(Product.brand).filter(
                Brand.brand_name == brand_name
            )

        product = query.first()

        if product is None:
            return jsonify({
                "reviews": [],
                "total": 0,
                "has_more": False
            }), 200

        reviews_query = Review.query.filter_by(
            product_id=product.product_id
        )

        total = reviews_query.count()

        reviews = (
            reviews_query
            .order_by(Review.review_id.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return jsonify({
            "reviews": [
                serialize_review(review)
                for review in reviews
            ],
            "total": total,
            "has_more": offset + len(reviews) < total
        }), 200

    except Exception:
        current_app.logger.exception(
            "Customer reviews retrieval failed"
        )
        return jsonify(error="Could not load reviews"), 500
