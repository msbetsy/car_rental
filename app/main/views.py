"""This module stores application views."""
import random
import os
from datetime import date, datetime, timedelta
from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename
from . import main
from .forms import ContactForm, OpinionForm, CalendarForm, NewsPostForm, CarForm
from .. import db
from ..models import User, Opinion, Car, NewsPost, Permission

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


def allowed_file(filename):
    """Check if file is allowed

    :param filename: The name of the file.
    :type filename: str
    :return: Information if file if allowed.
    :rtype: bool
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    return render_template("cars.html", current_user=current_user, all_cars=car_models, car_number=number_of_car_models,
                           permission=Permission.WRITE)


@main.route("/cars/add", methods=["GET", "POST"])
def add_model():
    form = CarForm()
    if form.validate_on_submit():
        file = form.image.data
        is_file = os.path.isfile(os.path.join(basedir, 'static\img\\', file.filename))
        filename = secure_filename(file.filename)
        if not is_file and allowed_file(file.filename):
            file.save(os.path.join(basedir, 'static\img\\', filename))
        new_car = Car(
            name=form.name.data,
            price=form.price.data,
            year=form.year.data,
            model=form.model.data,
            image=filename
        )
        db.session.add(new_car)
        db.session.commit()
        return redirect(url_for('main.show_models'))

    return render_template("new_car.html", form=form, current_user=current_user)


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
    posts = NewsPost.query.order_by(NewsPost.date.desc()).all()
    return render_template("news.html", current_user=current_user, all_posts=posts, permission=Permission.WRITE)


@main.route("/news/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post_to_show = NewsPost.query.get_or_404(post_id)
    is_file = os.path.isfile(os.path.join(basedir, 'static\img\\', post_to_show.img_url))
    if not is_file:
        post_to_show.img_url = "no_img.jpg"
    return render_template("post.html", post=post_to_show)


@main.route("/new-post", methods=["GET", "POST"])
@login_required
def add_new_post():
    form = NewsPostForm()
    if form.validate_on_submit():
        file = form.img_url.data
        is_file = os.path.isfile(os.path.join(basedir, 'static\img\\', file.filename))
        filename = secure_filename(file.filename)
        if not is_file and allowed_file(file.filename):
            file.save(os.path.join(basedir, 'static\img\\', filename))

        new_post = NewsPost(
            title=form.title.data,
            date=date.today().strftime("%Y-%m-%d"),
            body=form.news_text.data,
            author=current_user,
            img_url=filename
        )

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for('main.show_news'))

    return render_template("new_post.html", form=form, current_user=current_user)
