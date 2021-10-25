"""This module stores methods for users (API)."""
from flask import jsonify
from ..models import User
from . import api


@api.route('/users/', methods=['GET'])
def get_all_users():
    query = User.query.all()
    users = [user.to_json() for user in query]
    return jsonify({'data': users, 'number_of_records': len(query), 'success': True})


@api.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    query = User.query.get_or_404(id, description=f'User with id {id} not found')
    return jsonify({'data': query.to_json(), 'success': True})
