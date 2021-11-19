"""This module stores methods for authentication while using api."""
from flask import jsonify, request
from ..models import User, Permission, Role
from . import api
from app.api.errors import conflict, bad_request, unauthorized
from app.api.decorators import validate_json_content_type, token_required, permission_required
from .. import db


@api.route('/auth/register/', methods=['POST'])
@validate_json_content_type
def register():
    args = request.get_json()
    if 'email' not in args:
        return bad_request(message='No email')
    if User.query.filter(User.email == args['email']).first():
        return conflict(message=f'User with email {args["email"]} already exists')

    user = User.from_json(args)

    db.session.add(user)
    db.session.commit()

    token = user.generate_jwt_token()

    return jsonify({'success': True, 'token': token}), 201


@api.route('/auth/login/', methods=['POST'])
@validate_json_content_type
def login():
    args = request.get_json()
    if 'email' not in args:
        return bad_request(message='No email')
    if 'password' not in args:
        return bad_request(message='No password')
    user = User.query.filter(User.email == args['email']).first()

    if not user:
        return unauthorized(message='Invalid credentials')

    if not user.verify_password(args['password']):
        return unauthorized(message='Invalid credentials')

    token = user.generate_jwt_token()

    return jsonify({'success': True, 'token': token})


@api.route('/auth/about_me/', methods=['GET'])
@token_required
def get_current_user(user_id: int):
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    return jsonify({'success': True, 'data': user.to_json_user_data()})


@api.route('/auth/user/', methods=['PATCH'])
@token_required
@validate_json_content_type
def update_password_and_email(user_id: int):
    args = request.get_json()
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    if 'password' not in args:
        return bad_request(message='No password')
    if 'new_password' not in args and 'new_email' not in args:
        return bad_request(message='No new data')
    if not user.verify_password(args['password']):
        return unauthorized(message='Invalid password')
    else:
        if 'new_password' in args:
            user.password = args['new_password']
        if 'new_email' in args:
            query = User.query.filter_by(email=args['new_email']).first()
            if query:
                return conflict(message=f'Email {args["new_email"]} already exists')
            else:
                user.email = args['new_email']

    db.session.commit()

    return jsonify({'success': True})


@api.route('/auth/user/', methods=["PUT"])
@token_required
@validate_json_content_type
def update_user(user_id: int):
    args = request.get_json()
    user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')

    if 'email' in args:
        if User.query.filter(User.email == args['email']).first() is not None:
            return conflict(message=f'User with email {args["email"]} already exists')
        if 'password' not in args:
            return bad_request(message="No password, can't update email")
        else:
            if not user.verify_password(args['password']):
                return unauthorized(message='Invalid credentials, wrong password')

    if 'new_password' in args:
        if not user.verify_password(args['password']):
            return unauthorized(message='Invalid credentials, wrong password')

    User.update_from_json(user_id, args)
    db.session.commit()

    return jsonify({'success': True, 'data': user.to_json_user_data()})


@api.route('/auth/admin/', methods=["PUT"])
@token_required
@permission_required(Permission.ADMIN)
@validate_json_content_type
def update_user_by_admin(user_id: int):
    logged_user = User.query.get_or_404(user_id, description=f'User with id {user_id} not found')
    args = request.get_json()
    if 'user_to_edit_id' not in args:
        return bad_request(message='No user_to_edit_id')
    else:
        user_to_edit_id = args['user_to_edit_id']
        user = User.query.get_or_404(user_to_edit_id, description=f'User with id {user_to_edit_id} not found')
        if 'new_password' in args:
            del args['new_password']
        if 'password' in args:
            del args['password']
        if 'email' in args:
            if User.query.filter(User.email == args['email']).first() is not None:
                return conflict(message=f'User with email {args["email"]} already exists')

        if 'role_id' in args:
            if args['role_id'] in (1, 2, 3):
                user.role_id = args['role_id']
            else:
                return bad_request(message="Wrong role_id")

        User.update_from_json(user_to_edit_id, args)
        db.session.commit()
        role = Role.query.get(user.role_id).name

    return jsonify({'success': True, 'data': user.to_json_user_data(), 'role': role})
