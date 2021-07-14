"""This module stores application forms for authorization."""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User


class RegisterForm(FlaskForm):
    """Class used for registration new user.
    """
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Length(1, 80), Email()])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     EqualTo('password_check',
                                                             message='The passwords must be identical.')])
    password_check = PasswordField("Repeat the password", validators=[DataRequired()])
    telephone = StringField("Telephone", validators=[DataRequired()])
    submit = SubmitField("Sign me up")

    def validate_email(self, field):
        """Custom validator - non-duplicating email.

        :param field: The name of the field which will be validated.
        :type: wtforms.fields.core.StringField
        :raises ValidationError: Email duplicated.
        """
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email exists.')
