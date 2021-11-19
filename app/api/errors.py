"""This module stores methods for errors while using api."""
from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message, variable=None):
    if variable is None:
        response = jsonify({'error': 'bad request', 'message': message, 'success': False})
    else:
        response = jsonify({'error_value_key': variable, 'success': False,
                            'error': {'error': 'bad request', 'message': message}})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message, 'success': False})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message, 'success': False})
    response.status_code = 403
    return response


def conflict(message):
    response = jsonify({'error': 'conflict', 'message': message, 'success': False})
    response.status_code = 409
    return response


def unsupported_media_type(message):
    response = jsonify({'error': 'unsupported media type', 'message': message, 'success': False})
    response.status_code = 415
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    """Method used for validation new data."""
    return bad_request(e.args[0], e.args[1])
