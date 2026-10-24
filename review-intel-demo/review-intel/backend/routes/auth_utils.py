from flask import request
from flask_jwt_extended import verify_jwt_in_request


def require_auth():
    '''Attach to every protected blueprint with bp.before_request(require_auth).'''
    if request.method == 'OPTIONS':  # browser CORS preflight carries no token
        return None
    verify_jwt_in_request()
