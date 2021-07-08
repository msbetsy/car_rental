from flask import render_template, redirect, url_for
from flask_login import logout_user
from . import main


@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@main.route("/login")
def login():
    return render_template("login.html")


@main.route("/contact", methods=["GET", "POST"])
def contact():
    return render_template("contact.html")


@main.route("/register")
def register():
    return render_template("register.html")


@main.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('index'))


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
