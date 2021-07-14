"""This module stores application views for authorization."""
from flask import render_template, redirect, url_for
from flask_login import current_user, logout_user, login_user
from . import auth
from .forms import RegisterForm
from .. import db
from ..models import User


@auth.route("/login")
def login():
    return render_template("auth/login.html")


@auth.route("/user")
def show_user():
    pass


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
