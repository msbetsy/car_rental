"""This module stores methods for cars (API)."""
from flask import jsonify, request
from app.api.decorators import validate_json_content_type, token_required, permission_required
from app.api.errors import bad_request
from .query_features import apply_filter, apply_args_filter, get_args, get_pagination, sort_by
from ..models import Car, Permission
from . import api
from .. import db


@api.route('/cars/', methods=['GET'])
def get_all_cars():
    query = Car.query
    query = sort_by(query, Car)
    query = apply_filter(query, Car)
    cars_with_pagination, pagination = get_pagination(query, 'api.get_all_cars')
    params = request.args.get('params', "")
    cars = [get_args(car.to_json(), params) for car in cars_with_pagination]
    cars = apply_args_filter(cars)
    if request.args.get('page') or request.args.get('per_page'):
        return jsonify({'data': cars, 'number_of_records': len(cars), 'pagination': pagination, 'success': True})
    else:
        return jsonify({'data': cars, 'number_of_records': len(cars), 'success': True})


@api.route('/cars/<int:car_id>/', methods=['GET'])
def get_car(car_id: int):
    query = Car.query.get_or_404(car_id, description=f'Car with id {car_id} not found')
    params = request.args.get('params', "")
    car = get_args(query.to_json(), params)
    return jsonify({'data': car, 'success': True})


@api.route('/cars/', methods=['POST'])
@token_required
@permission_required(Permission.MODERATE)
@validate_json_content_type
def add_car(user_id: int):
    args = request.get_json()

    car = Car.from_json(args)
    db.session.add(car)
    db.session.commit()

    return jsonify({'success': True, 'data': car.to_json()}), 201


@api.route('/cars/', methods=['PUT'])
@token_required
@permission_required(Permission.MODERATE)
@validate_json_content_type
def edit_car(user_id: int):
    args = request.get_json()
    if 'car_to_edit_id' not in args:
        return bad_request(message='No car_to_edit_id')
    else:
        car_to_edit_id = args['car_to_edit_id']
        Car.update_from_json(car_to_edit_id, args)
        db.session.commit()
        car = Car.query.get(car_to_edit_id)
    return jsonify({'success': True, 'data': car.to_json()})
