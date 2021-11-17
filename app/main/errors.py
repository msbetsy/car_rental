"""This module stores error handlers for status codes."""
from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(403)
def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden', 'success': False})
        response.status_code = 403
        return response
    return render_template('status_codes/403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        if e.description != 'The requested URL was not found on the server. If you entered the URL manually please ' \
                            'check your spelling and try again.':
            response = jsonify({'error': e.description, 'success': False})
        else:
            response = jsonify({'error': 'not found', 'success': False})
        response.status_code = 404
        return response
    return render_template('status_codes/404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error', 'success': False})
        response.status_code = 500
        return response
    return render_template('status_codes/500.html'), 500
