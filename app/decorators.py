"""This module stores decorators used in application."""
from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(permission):
    """Check permission."""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def admin_required(f):
    """Check admin permission."""
    return permission_required(Permission.ADMIN)(f)


def moderator_required(f):
    """Check moderator permission."""
    return permission_required(Permission.MODERATE)(f)
