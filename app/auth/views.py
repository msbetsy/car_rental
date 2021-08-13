"""This module stores application views for authorization."""
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, logout_user, login_user
from . import auth
from .forms import RegisterForm, LoginForm
from .. import db
from ..models import User


@auth.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_user.data)
                session.permanent = True
                next = request.args.get('next')
                if next is None or not next.startswith('/'):
                    next = url_for('auth.login')
                    flash('You were successfully logged in')
                return redirect(next)

            else:
                flash('Password incorrect, please try again.')

        elif user is None:
            flash("That email does not exist, please register.")

    return render_template("auth/login.html", form=form, current_user=current_user)


@auth.route("/user", methods=["GET", "POST"])
def show_user():
    pass
    return render_template("auth/user.html", current_user=current_user)


@auth.route("/user/data", methods=["GET", "POST"])
def show_user_data():
    pass
    return render_template("auth/data.html", current_user=current_user)


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            password=form.password.data,
            telephone=form.telephone.data,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)

        return redirect(url_for('main.index'))
    return render_template("auth/register.html", form=form, current_user=current_user)


@auth.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('main.index'))
