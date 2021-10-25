from flask import abort, jsonify, request, current_app
import jwt
from ..models import User
from . import api
from app.api.decorators import validate_json_content_type
from .. import db


@api.route('/auth/register/', methods=['POST'])
@validate_json_content_type
def register():
    args = request.get_json()
    try:
        if User.query.filter(User.email == args['email']).first():
            abort(409, description=f'User with email {args["email"]} already exists')
    except KeyError:
        abort(400, description='No email')
    user = User.from_json(args)

    db.session.add(user)
    db.session.commit()

    token = user.generate_jwt_token()

    return jsonify({
        'success': True,
        'token': jwt.decode(token, current_app.config.get('SECRET_KEY'), algorithms='HS256')
    }), 201
