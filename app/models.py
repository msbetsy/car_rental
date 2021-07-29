"""This module stores models used in application."""
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey
from . import db, login_manager


class User(UserMixin, db.Model):
    """Class contains the user model --> the signed up person.
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    surname = db.Column(db.String(250), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(250), unique=False, nullable=False)
    telephone = db.Column(db.Integer, unique=False, nullable=False)
    opinions = relationship("Opinion", back_populates="opinion_author")
    car_rented = relationship('Rental', back_populates="users_rent")
    posts = relationship("NewsPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    @property
    def password(self):
        """A getter function for the password.

        :raises AttributeError: not readable attribute.
        """
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """A setter function for the password.

        :param password: User's password.
        :type: str
        """
        hash_and_salted_password = generate_password_hash(
            password,
            method='pbkdf2:sha256',
            salt_length=8
        )
        self.password_hash = hash_and_salted_password

    def verify_password(self, password):
        """Check if password is correct.

        :param password: User's password.
        :type: str
        :return: The information if the password matched.
        :rtype: bool
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Returns printable representation of User's class object.

        :return user_mail: User's email.
        :rtype: str
        """
        user_mail = '<User %r>' % self.email
        return user_mail


@login_manager.user_loader
def load_user(user_id):
    """Provides user session management - loading user.

    :param user_id: The ID of the user.
    :type: str
    :return: The corresponding user object.
    :rtype: class '__main__.User'
    """
    return User.query.get(int(user_id))


class Opinion(db.Model):
    """Class contains the opinion model --> opinions of logged in users.
    """
    __tablename__ = "opinions"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    opinion_author = relationship("User", back_populates="opinions")
    text = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)


class Car(db.Model):
    """Class contains information about the car model.
    """
    __tablename__ = "cars"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=False, nullable=False)
    price = db.Column(db.Float, unique=False, nullable=False)
    year = db.Column(db.Integer, unique=False, nullable=False)
    model = db.Column(db.String(250), unique=False, nullable=False)
    image = db.Column(db.Text, nullable=True)
    car_rental = relationship("Rental", back_populates="car_rent")


class Rental(db.Model):
    """Class contains information about rentals.
    """
    __tablename__ = 'rentals'
    cars_id = Column(ForeignKey('cars.id'), primary_key=True, nullable=False)
    users_id = Column(ForeignKey('users.id'), primary_key=True, nullable=False)
    from_date = db.Column(db.DateTime, primary_key=True, nullable=False)
    to_date = db.Column(db.DateTime, nullable=False)
    available_from = db.Column(db.DateTime, nullable=False)
    users_rent = relationship('User', back_populates="car_rented")
    car_rent = relationship("Car", back_populates="car_rental")


class NewsPost(db.Model):
    """Class contains NewsPosts.
    """
    __tablename__ = "news_posts"
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="posts")
    title = db.Column(db.String(250), unique=True, nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    comments = relationship("Comment", back_populates="parent_post")


class Comment(db.Model):
    """Class contains comments to NewsPosts.
    """
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey("news_posts.id"), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    parent_post = relationship("NewsPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")
    text = db.Column(db.Text, nullable=False)
