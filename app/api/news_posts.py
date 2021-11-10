"""This module stores methods for posts (API)."""
from flask import jsonify, request
from . import api
from ..models import NewsPost, Permission
from app.api.decorators import validate_json_content_type, token_required, permission_required
from app import db


@api.route('/posts/<int:post_id>/', methods=['GET'])
def show_post(post_id: int):
    query = NewsPost.query.get_or_404(post_id)
    return jsonify({'success': True, 'data': query.to_json()})


@api.route('/posts/', methods=['GET'])
def show_posts():
    query = NewsPost.query.all()
    posts = [post.to_json() for post in query]
    return jsonify({'success': True, 'data': posts})


@api.route('/posts/', methods=['POST'])
@token_required
@permission_required(Permission.MODERATE)
@validate_json_content_type
def add_post(user_id: int):
    args = request.get_json()
    args['author'] = user_id
    post = NewsPost.from_json(args)
    db.session.add(post)
    db.session.commit()
    return jsonify({'success': True, 'data': post.to_json()}), 201
