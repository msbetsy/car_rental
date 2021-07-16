"""This module stores application forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.fields.html5 import TelField
from wtforms.validators import DataRequired, Email, Length


class ContactForm(FlaskForm):
    """Class used for email contact.
    """
    name = StringField("Name", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Length(1, 80), Email()])
    telephone = TelField("Telephone", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")
