from flask import Blueprint, jsonify, request
from ..config import Config
from ..services.chatbot import ask
from .auth_utils import require_auth

bp = Blueprint('assistant', __name__, url_prefix='/api')
bp.before_request(require_auth)


@bp.post('/assistant')
def assistant():
    if not Config.ANTHROPIC_API_KEY:
        return jsonify(error='Chatbot is not configured (missing ANTHROPIC_API_KEY)'), 503
    data = request.get_json(silent=True) or {}
    question = (data.get('question') or '').strip()
    if not question or len(question) > 1000:
        return jsonify(error='Question must be 1-1000 characters'), 400
    history = [{'role': m['role'], 'content': m['content']}
               for m in (data.get('history') or [])[-6:]
               if m.get('role') in ('user', 'assistant') and isinstance(m.get('content'), str)]
    return jsonify(answer=ask(question, history))
