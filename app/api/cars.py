from flask import jsonify, request
from app.api.decorators import validate_json_content_type, token_required, permission_required
from ..models import Car, Permission
from . import api
from .. import db


@api.route('/cars/', methods=['GET'])
def get_all_cars():
    query = Car.query.all()
    cars = [car.to_json() for car in query]
    return jsonify({'data': cars, 'number_of_records': len(query), 'success': True})


@api.route('/cars/<int:car_id>', methods=['GET'])
def get_car(car_id: int):
    query = Car.query.get_or_404(car_id, description=f'Car with id {car_id} not found')
    return jsonify({'data': query.to_json(), 'success': True})


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
