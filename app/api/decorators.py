"""This module stores decorators for api."""
from functools import wraps
from flask import request, current_app
from werkzeug.exceptions import UnsupportedMediaType
import jwt
from app.api.errors import unauthorized, bad_request


def validate_json_content_type(func):
    """Check if content type is json."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        data = request.get_json()
        if data is None:
            raise UnsupportedMediaType('Content type must be: application/json')
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
