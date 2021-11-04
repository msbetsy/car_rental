"""This module stores methods for posts (API)."""
from flask import jsonify
from . import api
from ..models import NewsPost


@api.route('/posts/<int:post_id>', methods=['GET'])
def show_post(post_id: int):
    query = NewsPost.query.get_or_404(post_id)
    return jsonify({'success': True, 'data': ''})
