"""This module stores models used in application."""
from datetime import datetime, timedelta
import os
import shutil
import random
from flask_login import UserMixin, AnonymousUserMixin
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy import Column, ForeignKey
from werkzeug.utils import secure_filename
import jwt
from email_validator import validate_email, EmailNotValidError
from app.exceptions import ValidationError
from . import db, login_manager

BASEDIR = os.path.abspath(os.path.dirname(__file__))


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

    def to_json(self):
        """Convert user object to json.

        :return json_user: user's data in dict.
        :rtype: dict
        """
        opinions = [url_for('api.show_opinion', opinion_id=opinion.id) for opinion in
                    Opinion.query.filter_by(author_id=self.id).all()]
        comments = [url_for('api.show_comment', comment_id=comment.id) for comment in
                    Comment.query.filter_by(author_id=self.id).all()]
        user_rentals = [rental for rental in Rental.query.filter_by(users_id=self.id).all()]
        rentals = [
            url_for('api.show_rental', car_id=rental.cars_id, user_id=rental.users_id,
                    date_time=int(rental.from_date.strftime('%Y%m%d%H%M'))) for
            rental in user_rentals]
        posts = [url_for('api.show_post', post_id=post.id) for post in
                 NewsPost.query.filter_by(author_id=self.id).all()]

        json_user = {
            'name': self.name,
            'surname': self.surname,
            'post_number': len(self.posts),
            'posts': posts,
            'rentals_number': len(self.car_rented),
            'rentals': rentals,
            'comments_number': len(self.comments),
            'comments': comments,
            'opinions_number': len(self.opinions),
            'opinions': opinions
        }
        return json_user

    def to_json_user_data(self):
        """Convert user object to json, used for user not admin.

        :return json_user: user's data in dict.
        :rtype: dict
        """
        json_user = {
            'name': self.name,
            'surname': self.surname,
            'email': self.email,
            'telephone': self.telephone,
            'address': self.address
        }
        return json_user

    @staticmethod
    def from_json(json_data):
        """Create User object from json data.

        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        :return: User object.
        :rtype: object
        """
        name = json_data.get('name')
        surname = json_data.get('surname')
        email = json_data.get('email')
        password = json_data.get('password')
        telephone = json_data.get('telephone')
        try:
            address = json_data.get('address')
        except KeyError:
            address = None
        check_if_null(name, "name")
        check_if_null(surname, "surname")
        check_if_null(password, "password")
        check_if_null(email, "email")
        if len(email) > 80:
            raise ValidationError('Maximum number of characters is 80.', 'email')
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValidationError("Email is incorrect.", "email")
        check_if_null(telephone, "telephone")
        return User(name=name, surname=surname, password_hash=generate_password_hash(password), email=email,
                    telephone=telephone, address=address)

    @staticmethod
    def update_from_json(user_id, json_data):
        """Update User object from json data.

        :param user_id: User id.
        :type user_id: int
        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        """
        user = User.query.get_or_404(user_id)
        name = json_data.get('name', user.name)
        surname = json_data.get('surname', user.surname)
        email = json_data.get('email', user.email)
        telephone = json_data.get('telephone', user.telephone)

        if 'new_password' in json_data:
            password = json_data.get('new_password')
            check_if_null(password, "password")
            password_hash = generate_password_hash(password)
        else:
            password_hash = user.password_hash

        if 'address' in json_data:
            address = json_data.get('address', user.address)
            check_if_null(address, "address")
        else:
            address = user.address

        if len(email) > 80:
            raise ValidationError('Maximum number of characters is 80.', 'email')
        try:
            validate_email(email)
        except EmailNotValidError:
            raise ValidationError("Email is incorrect.", "email")
        check_if_null(name, "name")
        check_if_null(surname, "surname")
        check_if_null(email, "email")
        check_if_null(telephone, "telephone")

        user.name = name
        user.surname = surname
        user.password_hash = password_hash
        user.email = email
        user.telephone = telephone
        user.address = address

    def generate_jwt_token(self):
        """Generates jwt token.

        :return: JWT token.
        :rtype: str
        """
        payload = {
            'user_id': self.id,
            'exp': datetime.utcnow() + timedelta(minutes=current_app.config.get('JWT_EXPIRED_MINUTES', 10))
        }
        return jwt.encode(payload, current_app.config.get('SECRET_KEY'), algorithm='HS256')


def check_if_null(variable, variable_name):
    """Check if value in json dict is null or None.

    :param variable: Data from json.
    :type variable: any
    :param variable_name: Name of variable.
    :type variable_name: str
    :raises ValidationError: variable can't be null.
    """
    if variable is None or variable == '':
        raise ValidationError(f"{variable_name} can't be null", variable_name)


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

    def to_json(self):
        """Convert opinion object to json.

        :return json_opinion: data in dict.
        :rtype: dict
        """
        json_opinion = {
            "author_url": url_for('api.get_user', user_to_show_id=self.author_id),
            "name": User.query.get(self.author_id).name,
            "text": self.text,
            "image_url": url_for('static', filename='img/' + self.image),
            "date": self.date.strftime("%m/%d/%Y, %H:%M:%S")
        }
        return json_opinion

    @staticmethod
    def from_json(json_data):
        """Create Opinion object from json data.

        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        :return: Opinion object.
        :rtype: object
        """
        text = json_data.get('text')
        check_if_null(text, "text")
        date = datetime.today()
        pictures = ["opinion1.jpg", "opinion2.jpg", "opinion3.jpg"]
        image = random.choice(pictures)
        author = json_data.get('author')
        if not isinstance(text, str):
            raise ValidationError('Wrong value.', 'text')
        return Opinion(author_id=author, text=text, image=image, date=date)


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

    def to_json(self):
        """Convert car object to json.

        :return json_car: data in dict.
        :rtype: dict
        """
        img = url_for('static', filename='img/' + self.image)
        json_car = {
            'url': url_for('api.get_car', car_id=self.id),
            'name': self.name,
            'price': self.price,
            'year': self.year,
            'model': self.model,
            'image': img
        }
        return json_car

    @staticmethod
    def from_json(json_data):
        """Create Car object from json data.

        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        :return: Car object.
        :rtype: object
        """
        name = json_data.get('name')
        check_if_null(name, "name")

        price = json_data.get('price')
        check_if_null(price, "price")

        year = json_data.get('year')
        check_if_null(year, "year")

        model = json_data.get('model')
        check_if_null(model, "model")

        if 'image' in json_data:
            image = json_data.get('image')
            is_file = os.path.isfile(os.path.join(BASEDIR, 'static\img\\', os.path.basename(image)))
            filename = secure_filename(os.path.basename(image))
            if is_file:
                image = filename
            else:
                if filename.endswith(("png", "jpg", "jpeg", "gif")):
                    source = os.path.join(os.path.dirname(image), filename)
                    target = os.path.join(BASEDIR, 'static\img\\', filename)

                    try:
                        shutil.copyfile(source, target)
                        image = filename
                    except IOError as e:
                        raise ValidationError("Unable to copy file. %s" % e, 'image')
                else:
                    raise ValidationError('Wrong value, must be whole path , wrong format of file.', 'image')
        else:
            image = "403.jpg"

        if not isinstance(year, int) or year > datetime.today().year:
            raise ValidationError('Wrong value.', 'year')

        if not isinstance(price, (int, float)):
            raise ValidationError('Wrong value, must be numeric.', 'price')

        if not isinstance(name, str):
            raise ValidationError('Wrong value, must be string.', 'name')

        if not isinstance(model, str):
            raise ValidationError('Wrong value, must be string.', 'model')

        return Car(name=name, price=price, year=year, model=model, image=image)

    @staticmethod
    def update_from_json(car_id, json_data):
        """Update Car object from json data.

        :param car_id: Car id.
        :type car_id: int
        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        """
        car = Car.query.get_or_404(car_id)
        name = json_data.get('name', car.name)
        check_if_null(name, "name")
        price = json_data.get('price', car.price)
        check_if_null(price, "price")
        year = json_data.get('year', car.year)
        check_if_null(year, "year")
        model = json_data.get('model', car.model)
        check_if_null(model, "model")

        if 'image' in json_data:
            image = json_data.get('image')
            is_file = os.path.isfile(os.path.join(BASEDIR, 'static\img\\', os.path.basename(image)))
            filename = secure_filename(os.path.basename(image))
            if car.image != filename:
                if is_file:
                    image = filename
                else:
                    if filename.endswith(("png", "jpg", "jpeg", "gif")):
                        source = os.path.join(os.path.dirname(image), filename)
                        target = os.path.join(BASEDIR, 'static\img\\', filename)

                        try:
                            shutil.copyfile(source, target)
                            image = filename
                        except IOError as e:
                            raise ValidationError("Unable to copy file. %s" % e, 'image')
                    else:
                        raise ValidationError('Wrong value, must be whole path , wrong format of file.', 'image')
        else:
            image = car.image

        if not isinstance(year, int) or year > datetime.today().year:
            raise ValidationError('Wrong value.', 'year')

        if not isinstance(price, (int, float)):
            raise ValidationError('Wrong value, must be numeric.', 'price')

        if not isinstance(name, str):
            raise ValidationError('Wrong value, must be string.', 'name')

        if not isinstance(model, str):
            raise ValidationError('Wrong value, must be string.', 'model')

        car.name = name
        car.year = year
        car.price = price
        car.model = model
        car.image = image


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

    def to_json(self):
        """Convert rental object to json.

        :return json_rental: data in dict.
        :rtype: dict
        """
        json_rental = {
            'user_url': url_for('api.get_user', user_to_show_id=self.users_id),
            'car_url': url_for('api.get_car', car_id=self.cars_id),
            'from_date': self.from_date.strftime("%m/%d/%Y, %H:%M"),
            'to_date': self.to_date.strftime("%m/%d/%Y, %H:%M"),
            'available_from': self.available_from.strftime("%m/%d/%Y, %H:%M")
        }
        return json_rental

    @staticmethod
    def from_json(json_data):
        """Create Rental object from json data.

        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        :return: Rental object.
        :rtype: object
        """
        user_id = json_data.get('user_id')

        car = json_data.get('car_id')
        check_if_null(car, 'car_id')
        possible_car_id = [car.id for car in Car.query.all()]
        if car not in possible_car_id:
            raise ValidationError('Wrong value.', 'car_id')

        from_date = json_data.get('from_date')
        check_if_null(from_date, "from_date")
        from_date = check_date(from_date, "from_date")

        to_date = json_data.get('to_date')
        check_if_null(to_date, "to_date")
        to_date = check_date(to_date, "to_date")

        if to_date <= from_date:
            raise ValidationError(f"Wrong value, date can't be before {from_date.strftime('%Y-%m-%d %H:%M')}.",
                                  'from_date')
        all_car_rentals = [rental for rental in Rental.query.filter_by(cars_id=car).all()]
        for rental in all_car_rentals:
            if rental.from_date <= from_date <= rental.available_from or rental.from_date <= to_date + timedelta(
                    hours=1) <= rental.available_from:
                raise ValidationError(
                    f"Wrong dates, available before: "
                    f"{(rental.from_date + timedelta(minutes=-61)).strftime('%Y-%m-%d %H:%M')},"
                    f"available after:"
                    f"{(rental.available_from + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')}", "dates")
            if from_date < rental.from_date < rental.available_from and \
                    rental.from_date < rental.available_from < to_date + timedelta(hours=1):
                raise ValidationError(
                    f"Wrong dates, available before: "
                    f"{(rental.from_date + timedelta(minutes=-61)).strftime('%Y-%m-%d %H:%M')},"
                    f"available after:"
                    f"{(rental.available_from + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M')}", "dates")
        available_from = to_date + timedelta(hours=1)

        return Rental(cars_id=car, users_id=user_id, from_date=from_date, to_date=to_date,
                      available_from=available_from)


def check_date(date, name_date: str):
    """Check if check_date in json dict is correct.

    :param date: Date from json.
    :type date: int
    :param name_date: Name of date.
    :type name_date: str
    :raises ValidationError: variable is wrong.
    """
    if not isinstance(date, int):
        raise ValidationError('Wrong value, not int.', name_date)
    if len(str(date)) != 12:
        raise ValidationError('Wrong value, not 12 chars.', name_date)
    date_time_f = "".join((str(date), '00.000000'))
    try:
        date = datetime.strptime(date_time_f, '%Y%m%d%H%M%S.%f')
    except ValueError:
        raise ValidationError('Wrong value, not YmdHM format.', name_date)
    if date < datetime.now():
        raise ValidationError(f"Wrong value, date can't be before {datetime.now().strftime('%Y-%m-%d %H:%M')}.",
                              name_date)
    return date


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

    def to_json(self):
        """Convert NewsPost object to json.

        :return json_news_post: data in dict.
        :rtype: dict
        """
        comments_list = [comment for comment in Comment.query.filter_by(post_id=self.id).all()]
        comment_parents = list(
            set(([comment.parent_comment for comment in Comment.query.filter_by(post_id=self.id).all()])))
        comments = get_all_comments_for_post(parent_comment=0, list_of_comments=comments_list,
                                             list_of_parents_comments=comment_parents)
        json_news_post = {
            'user_url': url_for('api.get_user', user_to_show_id=self.author_id),
            'title': self.title,
            'text': self.body,
            'date': self.date,
            'img_url': url_for('static', filename='img/' + self.img_url),
            'comments_urls': comments
        }
        return json_news_post


def get_all_comments_for_post(parent_comment, list_of_comments, list_of_parents_comments):
    """Create a list of comments including hierarchy of child comments.

    :param parent_comment: Value of parent comment (ID).
    :type parent_comment: int
    :param list_of_comments: List of comments.
    :type list_of_comments: list
    :param list_of_parents_comments: List of parent comments (IDs).
    :type list_of_parents_comments: list
    :return all_comments: All comments with child comments.
    :rtype: list
    """
    all_comments = []
    for item in list_of_comments:
        if item.parent_comment == parent_comment:
            if item.id not in list_of_parents_comments:
                comment_url = url_for('api.show_comment', comment_id=item.id)
            else:
                comment_url = {
                    url_for('api.show_comment', comment_id=item.id): get_all_comments_for_post(item.id,
                                                                                               list_of_comments,
                                                                                               list_of_parents_comments)
                }
            all_comments.append(comment_url)
    return all_comments


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

    def to_json(self):
        """Convert comment object to json.

        :return json_comment: data in dict.
        :rtype: dict
        """
        if self.parent_comment == 0:
            upper_comment = None
        else:
            upper_comment = url_for('api.show_comment', comment_id=self.parent_comment)

        json_comment = {
            'text': self.text,
            'post_url': url_for('api.show_post', post_id=self.post_id),
            'author_url': url_for('api.get_user', user_to_show_id=self.author_id),
            'date': self.date.strftime("%m/%d/%Y, %H:%M:%S"),
            'upper_comment_url': upper_comment
        }

        return json_comment

    @staticmethod
    def from_json(json_data):
        """Create Comment object from json data.

        :param json_data: Data in json.
        :type json_data: dict
        :raises ValidationError: wrong attribute
        :return: Comment object.
        :rtype: object
        """
        text = json_data.get('text')
        check_if_null(text, "text")

        date = datetime.today()
        author = json_data.get('author')

        post = json_data.get('post_id')
        check_if_null(post, 'post_id')
        posts_number = len(NewsPost.query.all())

        upper_comment = json_data.get('upper_comment')
        check_if_null(upper_comment, "upper_comment")
        possible_upper_comments = [comment_id.id for comment_id in Comment.query.filter_by(post_id=post)]

        if not isinstance(text, str):
            raise ValidationError('Wrong value.', 'text')
        if not isinstance(post, int) or 0 > post or post > posts_number:
            raise ValidationError('Wrong value.', 'post')
        if not isinstance(upper_comment, int) or upper_comment < 1 or upper_comment not in possible_upper_comments:
            raise ValidationError('Wrong value.', 'upper_comment')

        return Comment(post_id=post, author_id=author, text=text, date=date, parent_comment=upper_comment)
