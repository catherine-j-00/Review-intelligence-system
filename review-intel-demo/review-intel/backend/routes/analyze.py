from flask import Blueprint, jsonify, request
from ..services.analysis_service import analyze_text
from .auth_utils import require_auth

bp = Blueprint('analyze', __name__, url_prefix='/api')
bp.before_request(require_auth)


@bp.post('/analyze-review')
def analyze():
    data = request.get_json(silent=True) or {}
    text = (data.get('review') or '').strip()
    if not text:
        return jsonify(error='review is required'), 400
    return jsonify(analyze_text(text))  # nothing is saved here
