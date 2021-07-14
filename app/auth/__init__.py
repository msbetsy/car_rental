"""The module contains the constructor of the package used to create blueprints for authorization operations."""
from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
