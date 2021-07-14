"""This module stores application views."""
from flask import render_template
from flask_login import current_user
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html", current_user=current_user)


@main.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html", current_user=current_user)


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
