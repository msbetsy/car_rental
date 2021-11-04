"""This module stores methods for comments (API)."""
from flask import jsonify
from . import api
from ..models import Comment


@api.route('/comments/', methods=['GET'])
def show_comments():
    query = Comment.query.all()
    comments = [comment.to_json() for comment in query]
    return jsonify({'success': True, 'data': comments})


@api.route('/comments/<int:comment_id>', methods=['GET'])
def show_comment(comment_id: int):
    query = Comment.query.get_or_404(comment_id)
    return jsonify({'success': True, 'data': query.to_json()})
