"""This module stores methods for posts (API)."""
from flask import jsonify
from . import api
from ..models import NewsPost


@api.route('/posts/<int:post_id>/', methods=['GET'])
def show_post(post_id: int):
    query = NewsPost.query.get_or_404(post_id)
    return jsonify({'success': True, 'data': query.to_json()})


@api.route('/posts/', methods=['GET'])
def show_posts():
    query = NewsPost.query.all()
    posts = [post.to_json() for post in query]
    return jsonify({'success': True, 'data': posts})
