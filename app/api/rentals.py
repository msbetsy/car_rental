"""This module stores methods for rentals (API)."""
from flask import jsonify, request
from datetime import datetime
from ..models import Rental, Permission, User
from . import api
from app.api.decorators import token_required, permission_required, validate_json_content_type
from .errors import bad_request
from .. import db


@api.route('/rentals/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def show_rentals():
    query = Rental.query.all()
    rentals = [rental.to_json() for rental in query]
    return jsonify({'success': True, 'data': rentals})


@api.route('/rentals/car<int:car_id>/user<int:user_id>/from<int:date_time>/', methods=['GET'])
@token_required
@permission_required(Permission.ADMIN)
def show_rental(users_id: int, car_id: int, user_id: int, date_time: int):
    date_time_f = "".join((str(date_time), '00.000000'))
    try:
        from_date = datetime.strptime(date_time_f, '%Y%m%d%H%M%S.%f')
    except ValueError:
        bad_request(message="Wrong from: acceptable format: YmdHM")
    query = Rental.query.get_or_404({"cars_id": car_id, "users_id": user_id, "from_date": from_date},
                                    description='Rental not found')

    return jsonify({'success': True, 'data': query.to_json()})


@api.route('/rentals/', methods=['POST'])
@token_required
@validate_json_content_type
def add_rental(user_id: int):
    args = request.get_json()
    if User.query.get(user_id).is_admin():
        if args.get('user_id_rental') is None:
            return bad_request(message="No user_id_rental, can't add rental")
        else:
            args['user_id'] = args.get('user_id_rental')
    else:
        args['user_id'] = user_id
    rental = Rental.from_json(args)
    db.session.add(rental)
    db.session.commit()
    return jsonify({'success': True, 'data': rental.to_json()}), 201


@api.route('/rentals/car<int:car_id>/user<int:user_id>/from<int:date_time>/', methods=['DELETE'])
@token_required
@permission_required(Permission.ADMIN)
def delete_rental(users_id: int, car_id: int, user_id: int, date_time: int):
    date_time_f = "".join((str(date_time), '00.000000'))
    try:
        from_date = datetime.strptime(date_time_f, '%Y%m%d%H%M%S.%f')
    except ValueError:
        return bad_request(message="Wrong from: acceptable format: YmdHM")
    query = Rental.query.get_or_404({"cars_id": car_id, "users_id": user_id, "from_date": from_date},
                                    description='Rental not found')
    db.session.delete(query)
    db.session.commit()
    return jsonify({'success': True})
