"""The module contains the constructor of the package used to create blueprints."""
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views
