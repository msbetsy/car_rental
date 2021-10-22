"""This module stores methods for errors while using api."""
from flask import jsonify
from app.exceptions import ValidationError
from . import api


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message, 'success': False})
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


@api.errorhandler(ValidationError)
def validation_error(e):
    """Method used for validation new data."""
    return bad_request(e.args[0])
