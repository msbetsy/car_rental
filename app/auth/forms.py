"""This module stores application forms for authorization."""
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo
from wtforms import ValidationError
from ..models import User, Role, Car


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


class LoginForm(FlaskForm):
    """Class used for log in user.
    """
    email = StringField("Email: ", validators=[DataRequired(), Length(1, 80), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_user = BooleanField('Remember me')
    submit = SubmitField("Log in")


class EditDataForm(FlaskForm):
    """Class used for edit user data.
    """
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    telephone = StringField("Telephone", validators=[DataRequired()])
    address = StringField("Address")
    submit = SubmitField("Save changes")


class EditMailForm(FlaskForm):
    """Class used for edit user mail.
    """
    new_email = StringField("", validators=[DataRequired(), Length(1, 80), Email()])
    password = PasswordField("", validators=[DataRequired()])
    submit_new_mail = SubmitField("Save changes")


class EditPasswordForm(FlaskForm):
    """Class used for edit user password.
    """
    old_password = PasswordField("", validators=[DataRequired()])
    new_password = PasswordField("", validators=[DataRequired(),
                                                 EqualTo('new_password_check',
                                                         message='The passwords must be identical.')])
    new_password_check = PasswordField("", validators=[DataRequired()])
    submit_new_password = SubmitField("Save changes")


class EditUserAdminForm(FlaskForm):
    """Class used for edit user by admin.
    """
    name = StringField("Name", validators=[DataRequired()])
    surname = StringField("Surname", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Length(1, 80), Email()])
    role = SelectField('Role', coerce=int)
    telephone = StringField("Telephone", validators=[DataRequired()])
    address = StringField("Address")
    submit = SubmitField("Save")

    def __init__(self, user, *args, **kwargs):
        super(EditUserAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        """Custom validator - non-duplicating email.

        :param field: The name of the field which will be validated.
        :type: wtforms.fields.core.StringField
        :raises ValidationError: Email duplicated.
        """
        if field.data != self.user.email and User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email exists.')


class AddReservationAdminForm(FlaskForm):
    """Class used for add new reservation by Admin.
    """
    name = SelectField('Rental', coerce=int)
    from_date_time = DateTimeField("From datetime", validators=[DataRequired()],
                                   render_kw={"placeholder": "yyyy-MM-DD HH:mm:ss"})
    to_date_time = DateTimeField("To datetime", validators=[DataRequired()],
                                 render_kw={"placeholder": "yyyy-MM-DD HH:mm:ss"})
    submit = SubmitField("Add")

    def __init__(self, *args, **kwargs):
        super(AddReservationAdminForm, self).__init__(*args, **kwargs)
        self.name.choices = [(car.id, car.name) for car in Car.query.order_by(Car.name).all()]

    def validate_from_date_time(self, field):
        """Custom validator - date is later then now.

        :param field: The name of the field which will be validated.
        :type: wtforms.fields.core.StringField
        :raises ValidationError: Datetime error.
        """
        if field.data <= datetime.now():
            raise ValidationError('Datetime error.')
