"""This module stores methods for opinions (API)."""
from flask import request, jsonify
from . import api
from ..models import Opinion
from .decorators import token_required, validate_json_content_type
from .. import db


@api.route('/opinions/', methods=['GET'])
def show_opinions():
    query = Opinion.query.all()
    opinions = [opinion.to_json() for opinion in query]
    return jsonify({'success': True, 'data': opinions})


@api.route('/opinions/<int:opinion_id>/', methods=['GET'])
def show_opinion(opinion_id: int):
    query = Opinion.query.get_or_404(opinion_id, description=f'Opinion with id {opinion_id} not found')
    return jsonify({'success': True, 'data': query.to_json()})


@api.route('/opinions/', methods=['POST'])
@token_required
@validate_json_content_type
def add_opinion(user_id: int):
    args = request.get_json()
    args['author'] = user_id
    opinion = Opinion.from_json(args)
    db.session.add(opinion)
    db.session.commit()

    return jsonify({"success": True, 'data': opinion.to_json()}), 201
