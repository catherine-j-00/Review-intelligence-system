from flask import Blueprint, jsonify
from ..database.models import Brand, Category, Product
from .auth_utils import require_auth

bp = Blueprint('lookups', __name__, url_prefix='/api')
bp.before_request(require_auth)


@bp.get('/brands')
def brands():
    rows = Brand.query.order_by(Brand.brand_name).all()
    return jsonify([{'brand_id': b.brand_id, 'brand_name': b.brand_name} for b in rows])


@bp.get('/categories')
def categories():
    rows = Category.query.order_by(Category.category_name).all()
    return jsonify([{'category_id': c.category_id, 'category_name': c.category_name} for c in rows])


@bp.get('/products')
def products():
    rows = Product.query.order_by(Product.product_name).all()
    return jsonify([{'product_id': p.product_id, 'product_name': p.product_name,
                     'brand': p.brand.brand_name if p.brand else None,
                     'category': p.category.category_name if p.category else None} for p in rows])
