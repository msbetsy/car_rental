"""This module stores models used in application."""
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey
from . import db, login_manager


class Permission:
    """Class contains the permission model --> each permission has different value.
    """
    COMMENT = 1
    WRITE = 2
    MODERATE = 4
    ADMIN = 8


class Role(db.Model):
    """Class contains the role model --> each role has different permissions.
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __init__(self, **kwargs):
        """The default value of the permission field will be 0.
        """
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        """Insert roles for users included in dict.
        """
        roles = {
            'User': [Permission.COMMENT],
            'Moderator': [Permission.COMMENT, Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.COMMENT, Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for item in roles:
            role = Role.query.filter_by(name=item).first()
            if role is None:
                role = Role(name=item)
            role.reset_permissions()
            for permission in roles[item]:
                role.add_permission(permission)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def has_permission(self, permission):
        """Checks if user has permission.

        :param permission: The name of the permission.
        :type permission: int
        :return: Information if object has permission.
        :rtype: bool
        """
        return self.permissions & permission == permission

    def add_permission(self, permission):
        """Add permission if user doesn't have one.

        :param permission: The name of the permission.
        :type permission: int
        """
        if not self.has_permission(permission):
            self.permissions += permission

    def remove_permission(self, permission):
        """Remove permission from user.

        :param permission: The name of the permission.
        :type permission: int
        """
        if self.has_permission(permission):
            self.permissions -= permission

    def reset_permissions(self):
        """Reset all user's permissions.
        """
        self.permissions = 0

    def __repr__(self):
        """Returns printable representation of Role's class object.

        :return name: Name of the role.
        :rtype: str
        """
        return '<Role %r>' % self.name


class AnonymousUser(AnonymousUserMixin):
    """Class used to check permissions for anonymous user.
    """

    def can(self, permission):
        """Checks if user has permission.

        :param permission: The name of the permission.
        :type permission: int
        :return: Information that user doesn't have permission.
        :rtype: bool
        """
        return False

    def is_admin(self):
        """Checks if user is admin.

        :return: Information that user isn't admin.
        :rtype: bool
        """
        return False


login_manager.anonymous_user = AnonymousUser


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
    address = db.Column(db.Text, nullable=True)
    opinions = relationship("Opinion", back_populates="opinion_author")
    car_rented = relationship('Rental', back_populates="users_rent")
    posts = relationship("NewsPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', name="fk_role_id"))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['CAR_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def can(self, permission):
        """Checks if user has permission.

        :param permission: The name of the permission.
        :type permission: int
        :return: Information if user has permission.
        :rtype: bool
        """
        return self.role is not None and self.role.has_permission(permission)

    def is_admin(self):
        """Check if user is admin.

        :return: The information if user is admin.
        :rtype: bool
        """
        return self.can(Permission.ADMIN)

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
        :type password: str
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
        :type password: str
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
    :type user_id: str
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
    date = db.Column(db.DateTime, nullable=False)
    parent_comment = db.Column(db.Integer, nullable=True)
