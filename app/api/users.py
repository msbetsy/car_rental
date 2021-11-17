"""This module stores methods for users (API)."""
from flask import jsonify, request
from ..models import User, Permission
from app.api.decorators import token_required, permission_required
from . import api
from .query_features import apply_filter, apply_args_filter, get_args, get_pagination, sort_by


@api.route('/users/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def get_all_users(user_id: int):
    query = User.query
    query = sort_by(query, User)
    query = apply_filter(query, User)
    users_with_pagination, pagination = get_pagination(query, 'api.get_all_users')
    params = request.args.get('params', "")
    users = [get_args(user.to_json(), params) for user in users_with_pagination]
    users = apply_args_filter(users)
    if request.args.get('per_page'):
        return jsonify({'data': users, 'number_of_records': len(users), 'pagination': pagination, 'success': True})
    else:
        return jsonify({'data': users, 'number_of_records': len(users), 'success': True})


@api.route('/users/<int:user_to_show_id>/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def get_user(user_id: int, user_to_show_id: int):
    query = User.query.get_or_404(user_to_show_id, description=f'User with id {user_to_show_id} not found')
    params = request.args.get('params', "")
    user = get_args(query.to_json(), params)
    return jsonify({'data': user, 'success': True})
