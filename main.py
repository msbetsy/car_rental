from flask import Flask, render_template
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/logout")
def logout():
    pass


@app.route("/news")
def show_news():
    pass


@app.route("/models")
def show_models():
    pass


@app.route("/pricing")
def show_pricing():
    pass


@app.route("/opinions")
def show_opinions():
    pass


if __name__ == "__main__":
    app.run(debug=True)
