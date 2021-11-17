"""This module stores methods for opinions (API)."""
from flask import request, jsonify
from . import api
from ..models import Opinion
from .decorators import token_required, validate_json_content_type
from .. import db
from .query_features import apply_filter, get_args, get_pagination, sort_by


@api.route('/opinions/', methods=['GET'])
def show_opinions():
    query = Opinion.query
    query = sort_by(query, Opinion)
    query = apply_filter(query, Opinion)
    opinions_with_pagination, pagination = get_pagination(query, 'api.show_opinions')
    params = request.args.get('params', "")
    opinions = [get_args(opinion.to_json(), params) for opinion in opinions_with_pagination]
    if request.args.get('per_page'):
        return jsonify(
            {'success': True, 'data': opinions, 'number_of_records': len(opinions), 'pagination': pagination})
    else:
        return jsonify({'data': opinions, 'number_of_records': len(opinions), 'success': True})


@api.route('/opinions/<int:opinion_id>/', methods=['GET'])
def show_opinion(opinion_id: int):
    query = Opinion.query.get_or_404(opinion_id, description=f'Opinion with id {opinion_id} not found')
    params = request.args.get('params', "")
    opinion = get_args(query.to_json(), params)
    return jsonify({'success': True, 'data': opinion})


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
