"""This module stores application forms."""
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.fields.html5 import TelField, DateField
from wtforms.validators import DataRequired, Email, Length
from wtforms_components import TimeField
from flask_ckeditor import CKEditorField


class ContactForm(FlaskForm):
    """Class used for email contact.
    """
    name = StringField("Name", validators=[DataRequired()])
    subject = StringField("Subject", validators=[DataRequired()])
    email = StringField("Email: ", validators=[DataRequired(), Length(1, 80), Email()])
    telephone = TelField("Telephone", validators=[DataRequired()])
    message = TextAreaField("Message", validators=[DataRequired()])
    submit = SubmitField("Send")


class OpinionForm(FlaskForm):
    """Class used for adding opinions.
    """
    opinion_text = TextAreaField("Add your opinion", validators=[DataRequired()])
    submit = SubmitField("Submit")


class CalendarForm(FlaskForm):
    """Class used for choosing date and time of car rental.
    """
    start_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField(format='%H:%M', validators=[DataRequired()])
    end_date = DateField(format='%Y-%m-%d', validators=[DataRequired()])
    end_time = TimeField(format='%H:%M', validators=[DataRequired()])
    submit = SubmitField("Submit")

    def validate(self):
        """Custom validator - check dates and time.

        :return: result of the validation if data is correct
        :rtype: boolean
        """
        if not super().validate():
            return False
        result = True
        if self.start_date.data > self.end_date.data:
            result = False
            self.start_date.errors.append("Start date is later than end date!")
        if self.start_date.data == self.end_date.data and self.start_time.data > self.end_time.data:
            result = False
            self.start_time.errors.append("Start time is later than end time!")

        return result


class NewsPostForm(FlaskForm):
    """Class used for adding new posts.
    """
    title = StringField("Title", validators=[DataRequired()])
    img_url = FileField("Image ", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'gif'], 'Images only!')])
    news_text = CKEditorField("Post", validators=[DataRequired()])
    submit = SubmitField("Submit")
