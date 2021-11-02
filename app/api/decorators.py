"""This module stores decorators for api."""
from functools import wraps
from flask import request, current_app
import jwt
from app.api.errors import unauthorized, bad_request, unsupported_media_type, forbidden
from ..models import User


def validate_json_content_type(func):
    """Check if content type is json."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            return unsupported_media_type(message='Content type must be: application/json')
        return func(*args, **kwargs)

    return wrapper


def token_required(func):
    """Token is required."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        token = None

        if 'Authorization' not in request.headers:
            return bad_request(message='No Authorization token')

        auth = request.headers.get('Authorization')

        if auth and 'Bearer ' in auth:
            token = auth.split(' ')[1]
        else:
            return bad_request(message='No token, log in or register')

        try:
            payload = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms='HS256')
        except jwt.ExpiredSignatureError:
            return unauthorized(message='Expired token. Login to get new one')
        except jwt.InvalidTokenError:
            return unauthorized(message='Invalid token. Please login or register')
        else:
            return func(payload['user_id'], *args, **kwargs)

    return wrapper


def permission_required(permission):
    """Check permissions"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = None
            auth = request.headers.get('Authorization')
            if 'Bearer ' in auth:
                token = auth.split(' ')[1]
            user_id = jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms='HS256')['user_id']
            if not User.query.get(user_id).can(permission):
                return forbidden('Insufficient permissions')
            return func(*args, **kwargs)

        return wrapper

    return decorator
