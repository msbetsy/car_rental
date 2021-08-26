"""This module stores application views for authorization."""
from datetime import datetime, timedelta
from flask import render_template, redirect, url_for, flash, request, session
from flask_login import current_user, logout_user, login_user, login_required
from . import auth
from .forms import RegisterForm, LoginForm, EditDataForm, EditMailForm, EditPasswordForm, EditUserAdminForm, \
    AddReservationAdminForm
from .. import db
from ..decorators import admin_required, moderator_required
from ..models import User, Rental, Role, Car, load_user


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
@login_required
def show_user():
    form_mail = EditMailForm()
    if form_mail.submit_new_mail.data and form_mail.validate_on_submit():
        if current_user.verify_password(form_mail.password.data):
            current_user.email = form_mail.new_email.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash('Changes saved.')
        else:
            flash('Wrong password')
        return redirect(url_for('.show_user'))

    form_password = EditPasswordForm()
    if form_password.submit_new_password.data and form_password.validate_on_submit():
        if current_user.verify_password(form_password.old_password.data):
            current_user.password = form_password.new_password.data
            db.session.add(current_user._get_current_object())
            db.session.commit()
            flash('Changes saved.')
        else:
            flash('Wrong password')
        return redirect(url_for('.show_user'))

    return render_template("auth/user.html", current_user=current_user, form_mail=form_mail,
                           form_password=form_password)


@auth.route("/user/data", methods=["GET", "POST"])
@login_required
def show_user_data():
    form = EditDataForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.surname = form.surname.data
        current_user.telephone = form.telephone.data
        if len(form.address.data) != 0:
            current_user.address = form.address.data
        else:
            current_user.address = None
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('Changes saved.')
        return redirect(url_for('.show_user_data'))
    form.name.data = current_user.name
    form.surname.data = current_user.surname
    form.telephone.data = current_user.telephone
    form.address.data = current_user.address
    return render_template("auth/data.html", current_user=current_user, form=form)


@auth.route("/user/reservations", methods=["GET", "POST"])
@login_required
def show_user_reservations():
    reservations = Rental.query.filter_by(users_id=current_user.id).all()
    return render_template("auth/reservations.html", current_user=current_user, reservations=reservations)


@auth.route("/users", methods=["GET", "POST"])
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template("auth/users.html", current_user=current_user, users=users)


@auth.route("/edit-user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_user_admin(user_id):
    user = User.query.get_or_404(user_id)
    form = EditUserAdminForm(user=user)
    if form.validate_on_submit():
        user.name = form.name.data
        user.surname = form.surname.data
        user.email = form.email.data
        user.role = Role.query.get(form.role.data)
        user.telephone = form.telephone.data
        user.address = form.address.data
        db.session.add(user)
        db.session.commit()
        flash('The profile has been updated.')
        return redirect(url_for('auth.users'))
    form.name.data = user.name
    form.surname.data = user.surname
    form.email.data = user.email
    form.role.data = user.role_id
    form.telephone.data = user.telephone
    form.address.data = user.address
    return render_template("auth/edit_user_admin.html", current_user=current_user, user=user, form=form)


@auth.route("/user/<int:user_id>/reservations", methods=["GET", "POST"])
@login_required
@admin_required
def show_user_reservations_admin(user_id):
    reservations = Rental.query.filter_by(users_id=user_id).all()
    return render_template("auth/edit_reservations_admin.html", current_user=current_user, reservations=reservations)


@auth.route("/user/reservations/add/user/<int:user_id>", methods=["GET", "POST"])
@login_required
@admin_required
def add_reservation(user_id):
    form = AddReservationAdminForm()
    user = load_user(user_id)
    if form.validate_on_submit():
        car = Car.query.get(form.name.data)
        reservations = Rental.query.filter_by(cars_id=car.id, users_id=user.id).all()
        if form.from_date_time.data >= form.to_date_time.data:
            flash("Dates Error!")
        else:
            if len(reservations) == 0:
                new_reservation = Rental(cars_id=car.id, users_id=user.id, from_date=form.from_date_time.data,
                                         to_date=form.to_date_time.data,
                                         available_from=form.to_date_time.data + timedelta(hours=1))
                db.session.add(new_reservation)
                db.session.commit()
                flash('Reservation added.')
                return redirect(url_for('auth.show_user_reservations_admin', user_id=user_id))
            else:
                for reservation in reservations:
                    available_date = False
                    rental_from = form.from_date_time.data
                    rental_to = form.to_date_time.data + timedelta(hours=1)
                    if reservation.from_date <= rental_from <= reservation.available_from or \
                            reservation.from_date <= rental_to <= reservation.available_from:
                        flash("Change dates!")
                        flash(
                            " ".join(("Available before: ", str(reservation.from_date + timedelta(minutes=-61))[:-3])))
                        flash(" ".join(
                            ("Available after: ", str(reservation.available_from + timedelta(minutes=1))[:-3])))
                        break
                    else:
                        available_date = True

                    if rental_from < reservation.from_date < reservation.available_from and \
                            reservation.from_date < reservation.available_from < rental_to:
                        available_date = False
                        flash("Change dates!")
                        flash(" ".join(("Available before:", str(reservation.from_date + timedelta(minutes=-61))[:-3])))
                        flash(" ".join(
                            ("Available after: ", str(reservation.available_from + timedelta(minutes=1))[:-3])))
                        break

                    if available_date:
                        new_reservation = Rental(cars_id=car.id, users_id=user.id, from_date=form.from_date_time.data,
                                                 to_date=form.to_date_time.data,
                                                 available_from=form.to_date_time.data + timedelta(hours=1))

                        db.session.add(new_reservation)
                        db.session.commit()
                        flash("Reservation saved!")
                        return redirect(url_for('auth.show_user_reservations_admin', user_id=user_id))

    return render_template("auth/new_reservation.html", current_user=current_user, form=form)


@auth.route("/user/reservations/delete", methods=["GET", "POST"])
@login_required
@admin_required
def delete_user_reservation():
    if request.method == 'POST':
        car_id = int(request.form.get('car_id'))
        user_id = int(request.form.get('user_id'))
        try:
            from_date = datetime.strptime(request.form.get('from_date'), "%Y-%m-%d %H:%M:%S.%f")
            reservation = Rental.query.get({"cars_id": car_id, "users_id": user_id, "from_date": from_date})
        except ValueError:
            from_date = datetime.strptime(request.form.get('from_date'), "%Y-%m-%d %H:%M:%S")
            reservation = Rental.query.get({"cars_id": car_id, "users_id": user_id, "from_date": from_date})
        db.session.delete(reservation)
        db.session.commit()
        flash('Deleted')
        return redirect(url_for('auth.show_user_reservations_admin', user_id=user_id))
    return render_template("auth/edit_reservations_admin.html", current_user=current_user)


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
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
