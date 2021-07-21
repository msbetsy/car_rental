"""This module stores application configuration settings."""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Class contains general application configuration settings.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY_CAR") or 'sjk897JH7KH65#(@&'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REMEMBER_COOKIE_DURATION = timedelta(minutes=10)
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)

    @staticmethod
    def init_app(app):
        """Allows the application to customize its own configuration.

        :param app: Flask application.
        :type: class 'flask.app.Flask
        """
        pass


class DevelopmentConfig(Config):
    """Class contains development configuration settings."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'db.sqlite')


config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
