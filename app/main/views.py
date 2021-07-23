"""This module stores application views."""
import random
from datetime import datetime
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from . import main
from .forms import ContactForm, OpinionForm
from .. import db
from ..models import User, Opinion


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


@main.route("/opinions", methods=["GET", "POST"])
def add_opinion():
    pictures = ["opinion1.jpg", "opinion2.jpg", "opinion3.jpg"]
    opinions = db.session.query(Opinion.text, Opinion.image, Opinion.date, User.name).filter(
        Opinion.author_id == User.id).order_by(Opinion.date.desc())
    number_of_opinions = db.session.query(Opinion).count()
    form = OpinionForm()
    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash("You need to login or register to add opinion.")
            return redirect(url_for("auth.login"))
        new_opinion = Opinion(
            text=form.opinion_text.data,
            opinion_author=current_user,
            image=random.choice(pictures),
            date=datetime.today()
        )
        db.session.add(new_opinion)
        db.session.commit()
        flash("Thank you for your feedback.")
        return redirect(url_for('main.add_opinion'))

    return render_template("opinions.html", form=form, current_user=current_user, all_opinions=opinions,
                           all_pictures=pictures, opinions_number=number_of_opinions)
