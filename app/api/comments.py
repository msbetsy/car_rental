"""This module stores methods for comments (API)."""
from flask import jsonify, request
from app.api.decorators import token_required, validate_json_content_type
from .query_features import apply_filter, get_args, get_pagination, sort_by
from . import api
from ..models import Comment
from .. import db


@api.route('/comments/', methods=['GET'])
def show_comments():
    query = Comment.query
    query = sort_by(query, Comment)
    query = apply_filter(query, Comment)
    comments_with_pagination, pagination = get_pagination(query, 'api.show_comments')
    params = request.args.get('params', "")
    comments = [get_args(comment.to_json(), params) for comment in comments_with_pagination]
    if request.args.get('per_page'):
        return jsonify(
            {'data': comments, 'number_of_records': len(comments), 'pagination': pagination, 'success': True})
    else:
        return jsonify({'data': comments, 'number_of_records': len(comments), 'success': True})


@api.route('/comments/<int:comment_id>/', methods=['GET'])
def show_comment(comment_id: int):
    query = Comment.query.get_or_404(comment_id, description=f'Comment with id {comment_id} not found')
    params = request.args.get('params', "")
    comment = get_args(query.to_json(), params)
    return jsonify({'success': True, 'data': comment})


@api.route('/comments/', methods=['POST'])
@token_required
@validate_json_content_type
def add_comment(user_id: int):
    args = request.get_json()
    args['author'] = user_id
    comment = Comment.from_json(args)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'success': True, 'data': comment.to_json()}), 201
