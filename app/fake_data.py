"""This module creates fake data."""
import random
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from faker import Faker

from . import db
from .models import User, Opinion


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


def opinions(count=10):
    """Add fake opinions to db - Opinion model"""

    fake = Faker()
    i = 0
    imagines = ["opinion1.jpg", "opinion2.jpg", "opinion3.jpg"]
    while i < count:
        date_str = fake.date()
        users_id = [item[0] for item in User.query.with_entities(User.id).all()]
        opinion = Opinion(author_id=random.choice(users_id), text=fake.sentence(), image=random.choice(imagines),
                          date=datetime.strptime(date_str, '%Y-%m-%d').date())
        db.session.add(opinion)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
