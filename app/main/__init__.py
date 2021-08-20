"""The module contains the constructor of the package used to create blueprints."""
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


@main.app_context_processor
def inject_permissions():
    """Show Permission constants in all templates."""
    return dict(Permission=Permission)
