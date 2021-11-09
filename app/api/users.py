"""This module stores methods for users (API)."""
from flask import jsonify
from ..models import User, Permission
from app.api.decorators import token_required, permission_required
from . import api


@api.route('/users/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def get_all_users(user_id: int):
    query = User.query.all()
    users = [user.to_json() for user in query]
    return jsonify({'data': users, 'number_of_records': len(query), 'success': True})


@api.route('/users/<int:user_to_show_id>/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def get_user(user_id: int, user_to_show_id: int):
    query = User.query.get_or_404(user_to_show_id, description=f'User with id {user_to_show_id} not found')
    return jsonify({'data': query.to_json(), 'success': True})
