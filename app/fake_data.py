"""This module creates fake data."""
from sqlalchemy.exc import IntegrityError
from faker import Faker

from . import db
from .models import User


def users(count=10):
    """Add fake users to db - User model"""
    fake = Faker()
    i = 0
    while i < count:
        name = fake.name().split()
        user = User(name=name[0],
                    surname=name[1],
                    email=fake.email(),
                    password_hash='password',
                    telephone=fake.phone_number())
        db.session.add(user)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
