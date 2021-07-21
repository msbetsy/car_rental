"""This module stores application views."""
from flask import render_template
from flask_login import current_user
from . import main
from .forms import ContactForm


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", current_user=current_user)


@main.route("/contact", methods=["GET", "POST"])
def contact():
    if current_user.is_anonymous:
        form = ContactForm()
    else:
        form = ContactForm(name=" ".join((current_user.name, current_user.surname)), email=current_user.email,
                           telephone=current_user.telephone)
    if form.validate_on_submit():
        return render_template("contact.html", form=form, success=True, current_user=current_user)
    return render_template("contact.html", form=form, current_user=current_user)


@main.route("/news")
def show_news():
    pass


@main.route("/models")
def show_models():
    pass


@main.route("/pricing")
def show_pricing():
    pass


@main.route("/opinions")
def show_opinions():
    pass
