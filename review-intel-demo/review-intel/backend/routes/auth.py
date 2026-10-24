from datetime import timedelta
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from ..database.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.post('/login')
def login():
    data = request.get_json(silent=True) or {}
    user = User.query.filter_by(username=data.get('username', '')).first()
    if not user or not user.check_password(data.get('password', '')):
        return jsonify(error='Invalid credentials'), 401
    token = create_access_token(identity=user.username, expires_delta=timedelta(hours=8))
    return jsonify(access_token=token)
