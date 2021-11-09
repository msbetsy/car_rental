"""This module stores methods for comments (API)."""
from flask import jsonify, request
from . import api
from ..models import Comment
from .. import db
from app.api.decorators import token_required, validate_json_content_type


@api.route('/comments/', methods=['GET'])
def show_comments():
    query = Comment.query.all()
    comments = [comment.to_json() for comment in query]
    return jsonify({'success': True, 'data': comments})


@api.route('/comments/<int:comment_id>/', methods=['GET'])
def show_comment(comment_id: int):
    query = Comment.query.get_or_404(comment_id)
    return jsonify({'success': True, 'data': query.to_json()})


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
