from flask import jsonify, request
from ..models import User
from . import api
from app.api.errors import conflict, bad_request, unauthorized
from app.api.decorators import validate_json_content_type
from .. import db


@api.route('/auth/register/', methods=['POST'])
@validate_json_content_type
def register():
    args = request.get_json()
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
