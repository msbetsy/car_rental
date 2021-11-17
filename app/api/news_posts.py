"""This module stores methods for posts (API)."""
from flask import jsonify, request
from . import api
from ..models import NewsPost, Permission
from app.api.decorators import validate_json_content_type, token_required, permission_required
from app import db
from .query_features import apply_filter, apply_args_filter, get_args, get_pagination, sort_by


@api.route('/posts/<int:post_id>/', methods=['GET'])
def show_post(post_id: int):
    query = NewsPost.query.get_or_404(post_id, description=f'Post with id {post_id} not found')
    params = request.args.get('params', "")
    post = get_args(query.to_json(), params)
    return jsonify({'success': True, 'data': post})


@api.route('/posts/', methods=['GET'])
def show_posts():
    query = NewsPost.query
    query = sort_by(query, NewsPost)
    query = apply_filter(query, NewsPost)
    posts_with_pagination, pagination = get_pagination(query, 'api.show_posts')
    params = request.args.get('params', "")
    posts = [get_args(post.to_json(), params) for post in posts_with_pagination]
    posts = apply_args_filter(posts)
    if request.args.get('per_page'):
        return jsonify({'success': True, 'data': posts, 'number_of_records': len(posts), 'pagination': pagination})
    else:
        return jsonify({'success': True, 'data': posts, 'number_of_records': len(posts)})


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
