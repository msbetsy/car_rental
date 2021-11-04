"""The module contains the constructor of the package used to create blueprints for api."""
from flask import Blueprint

api = Blueprint('api', __name__)

from . import errors, users, authentication, cars, comments, news_posts
