"""This module stores application views."""
import random
from datetime import datetime, timedelta
from flask import render_template, flash, url_for, redirect
from flask_login import current_user
from . import main
from .forms import ContactForm, OpinionForm, CalendarForm, NewsPostForm
from .. import db
from ..models import User, Opinion, Car, NewsPost


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


@main.route("/cars")
def show_models():
    car_models = Car.query.all()
    number_of_car_models = len(car_models)
    return render_template("cars.html", current_user=current_user, all_cars=car_models, car_number=number_of_car_models)


@main.route("/cars/<string:car_name>", methods=["GET", "POST"])
def show_car(car_name):
    car_to_show = Car.query.filter_by(name=car_name).first()
    rental_list = car_to_show.car_rental
    form = CalendarForm()
    if form.validate_on_submit():
        from_date = form.start_date.data
        from_time = form.start_time.data
        to_date = form.end_date.data
        to_time = form.end_time.data
        from_datetime = datetime.strptime(" ".join((str(from_date), str(from_time))), '%Y-%m-%d %H:%M:%S')
        to_datetime = datetime.strptime(" ".join((str(to_date), str(to_time))), '%Y-%m-%d %H:%M:%S')
        if len(rental_list) != 0:
            for element in rental_list:
                datetime_available_from = element.from_date + timedelta(minutes=-61)
                if datetime_available_from <= from_datetime <= element.available_from or \
                        datetime_available_from <= to_datetime <= element.available_from:
                    flash("Change dates!")
                    flash(" ".join(("Available before: ", str(element.from_date + timedelta(minutes=-61))[:-3])))
                    flash(" ".join(("Available after: ", str(element.available_from + timedelta(minutes=1))[:-3])))

                if datetime_available_from < datetime_available_from < to_datetime or \
                        datetime_available_from < element.available_from < to_datetime:
                    flash("Change dates!")
                    flash(" ".join(("Available before:", str(element.from_date + timedelta(minutes=-61))[:-3])))
                    flash(" ".join(("Available after: ", str(element.available_from + timedelta(minutes=1))[:-3])))
    return render_template("car.html", form=form, car=car_to_show, current_user=current_user, car_name=car_name)


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


@main.route("/news")
def show_news():
    posts = NewsPost.query.all()
    return render_template("news.html", current_user=current_user, all_posts=posts)
