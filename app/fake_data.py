"""This module creates fake data."""
import random
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError
from faker import Faker

from . import db
from .models import User, Opinion, Car, Rental, NewsPost, Comment


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
    images = ["opinion1.jpg", "opinion2.jpg", "opinion3.jpg"]
    users_id = [item[0] for item in User.query.with_entities(User.id).all()]
    while i < count:
        date_str = fake.date()
        opinion = Opinion(author_id=random.choice(users_id), text=fake.sentence(), image=random.choice(images),
                          date=datetime.strptime(date_str, '%Y-%m-%d').date())
        db.session.add(opinion)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def cars(count=10):
    """Add fake car models to db - Car model."""
    fake = Faker()
    i = 0
    images = ["car1.jpg", "car2.jpg", "car3.jpg"]
    while i < count:
        car = Car(name=fake.word(), price=fake.random_int(), year=fake.year(), model=fake.word(),
                  image=random.choice(images))
        db.session.add(car)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def rentals(count=10):
    """Add fake rentals to db - Rental model."""
    fake = Faker()
    i = 0
    cars_id = [item[0] for item in Car.query.with_entities(Car.id).all()]
    users_id = [item[0] for item in User.query.with_entities(User.id).all()]
    dates = []
    while len(dates) < count:
        possible_rental_from = fake.date_time()
        if possible_rental_from not in dates:
            dates.append(possible_rental_from)
    while i < count:
        rental_from = dates[i]
        rental_to = fake.date_time_between_dates(datetime_start=rental_from,
                                                 datetime_end=rental_from + timedelta(days=10))
        available_date = rental_to + timedelta(hours=1)
        rent = Rental(cars_id=random.choice(cars_id), users_id=random.choice(users_id),
                      from_date=rental_from, to_date=rental_to,
                      available_from=available_date)
        db.session.add(rent)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def posts(count=10):
    """Add fake posts to db - NewsPost model."""
    fake = Faker()
    i = 0
    images = ["car1.jpg", "car2.jpg", "car3.jpg"]
    users_id = [item[0] for item in User.query.with_entities(User.id).all()]
    titles = []
    while len(titles) < count:
        possible_title = fake.sentence()
        if possible_title not in titles:
            titles.append(possible_title)
    while i < count:
        post = NewsPost(author_id=random.choice(users_id), title=titles[i], date=fake.date(), body=fake.text(),
                        img_url=random.choice(images))
        db.session.add(post)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def comments(count=30):
    """Add fake comments to db - Comments model."""
    fake = Faker()
    i = 0
    users_id = [item[0] for item in User.query.with_entities(User.id).all()]
    posts_id = [item[0] for item in NewsPost.query.with_entities(NewsPost.id).all()]
    while i < count:
        comment = Comment(post_id=random.choice(posts_id), author_id=random.choice(users_id), text=fake.text(),
                          date=fake.date_time(), parent_comment=0)
        db.session.add(comment)
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()
