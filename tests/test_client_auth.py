"""This module stores tests for client app.auth routes."""
import unittest
import re
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.models import Role, User, Rental, Car
from tests.api_functions import create_user, create_admin, create_moderator, check_login_required_must_login, \
    check_admin_or_moderator_required

register_invalid_data = [
    ({"surname": "surname", "email": "mail@mail.com", "password": "password", "password_check": "password",
      "telephone": "123"}, "name"),
    ({"name": "name", "email": "mail@mail.com", "password": "password", "password_check": "password",
      "telephone": "123"}, "surname"),
    ({"name": "name", "surname": "surname", "password": "password", "password_check": "password",
      "telephone": "123"}, "email"),
    ({"name": "name", "surname": "surname", "email": "mail.mail.com", "password": "password",
      "password_check": "password", "telephone": "123"}, "email_invalid"),
    ({"name": "name", "surname": "surname",
      "email": "mailmailmailmailmailmailmailmailmailmailmailmailmailmailmailmailmailmailmailmail@mail.com",
      "password": "password", "password_check": "password", "telephone": "123"}, "email_too_long"),
    ({"name": "name", "surname": "surname", "email": "mail@mail.com", "password_check": "password", "telephone": "123"},
     "password"),
    ({"name": "name", "surname": "surname", "email": "mail@mail.com", "password": "password",
      "password_check": "password2", "telephone": "123"}, "password"),
    ({"name": "name", "surname": "surname", "email": "mail@mail.com", "password": "password",
      "password_check": "password"}, "telephone"),
    ({"name": "name", "surname": "surname", "email": "test@test.com", "password": "password",
      "password_check": "password", "telephone": "123"}, "email_exists")
]


def change_date_to_str(date):
    """Change datetime to string format.
    :param date: Datetime
    :type date: datetime
    :return: Datetime in format %Y-%m-%d %H:%M:%S
    :rtype: str"""
    return date.strftime("%Y-%m-%d %H:%M:%S")


class FlaskClientAuthTestCase(unittest.TestCase):
    """Test all routes for app.auth."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        self.user = create_user()
        self.user_admin = create_admin()
        self.user_moderator = create_moderator()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def register(self, name, surname, email, password, password_check, telephone):
        """Function for register user.

        :param name: User's name
        :type name: str
        :param surname: User's surname
        :type surname: str
        :param email: User's email
        :type email: str
        :param password: User's password
        :type password: str
        :param password_check: User's password
        :type password_check: str
        :param telephone: User's telephone
        :type telephone: int
        :return: Response for the register query
        :rtype: flask.wrappers.Response
        """
        return self.client.post('/auth/register',
                                data={
                                    'name': name, 'surname': surname, 'email': email, 'password': password,
                                    'password_check': password_check,
                                    'telephone': telephone},
                                follow_redirects=True
                                )

    def login(self, email, password):
        """Function for login user.

        :param email: User's email
        :type email: str
        :param password: User's password
        :type password: str
        :return: Response for the login query
        :rtype: flask.wrappers.Response
        """
        return self.client.post('/auth/login', data=dict(email=email, password=password), follow_redirects=True)

    # Check pages @admin_required decorator
    def test_admin_required_decorator(self):
        """Test all routes with admin_required decorator."""
        user_id = 1
        responses = [self.login('test@test.com', 'password'), self.login('moderator@test.com', 'password')]
        for _ in responses:
            # Test users function from app.auth.views
            check_admin_or_moderator_required(self.client.get, '/auth/users', self.assertEqual, self.assertIn,
                                              self.assertNotIn)
            # Test edit_user_admin function from app.auth.views
            check_admin_or_moderator_required(self.client.get, f'/auth/edit-user/{user_id}', self.assertEqual,
                                              self.assertIn, self.assertNotIn)
            # Test show_user_reservations_admin function from app.auth.views
            check_admin_or_moderator_required(self.client.get, f'/auth/user/{user_id}/reservations', self.assertEqual,
                                              self.assertIn, self.assertNotIn)
            # Test add_reservation function from app.auth.views
            check_admin_or_moderator_required(self.client.get, f'/auth/user/reservations/add/user/{user_id}',
                                              self.assertEqual, self.assertIn, self.assertNotIn)
            # Test delete_user_reservation function from app.auth.views
            check_admin_or_moderator_required(self.client.get, '/auth/user/reservations/delete', self.assertEqual,
                                              self.assertIn, self.assertNotIn)

    # Check pages @login_required decorator
    def test_login_required_decorator(self):
        """Test all routes with login_required decorator."""
        user_id = 1

        # Test show_user function from app.auth.views
        check_login_required_must_login(self.client.post, '/auth/user', self.assertEqual, self.assertIn)

        # Test show_user_data function from app.auth.views
        check_login_required_must_login(self.client.get, '/auth/user/data', self.assertEqual, self.assertIn)
        check_login_required_must_login(self.client.post, '/auth/user/data', self.assertEqual, self.assertIn)

        # Test show_user_reservations function from app.auth.views
        check_login_required_must_login(self.client.get, '/auth/user/reservations', self.assertEqual, self.assertIn)

        # Test logout function from app.auth.views
        check_login_required_must_login(self.client.get, '/auth/logout', self.assertEqual, self.assertIn)

        # Test users function from app.auth.views
        check_login_required_must_login(self.client.get, '/auth/users', self.assertEqual, self.assertIn)

        # Test edit_user_admin function from app.auth.views
        check_login_required_must_login(self.client.get, f'/auth/edit-user/{user_id}', self.assertEqual, self.assertIn)

        # Test show_user_reservations_admin function from app.auth.views
        check_login_required_must_login(self.client.get, f'/auth/user/{user_id}/reservations', self.assertEqual,
                                        self.assertIn)

        # Test add_reservation function from app.auth.views
        check_login_required_must_login(self.client.get, f'/auth/user/reservations/add/user/{user_id}',
                                        self.assertEqual, self.assertIn)
        check_login_required_must_login(self.client.post, f'/auth/user/reservations/add/user/{user_id}',
                                        self.assertEqual, self.assertIn)

        # Test delete_user_reservation function from app.auth.views
        check_login_required_must_login(self.client.get, f'/auth/user/reservations/delete', self.assertEqual,
                                        self.assertIn)
        check_login_required_must_login(self.client.post, f'/auth/user/reservations/delete', self.assertEqual,
                                        self.assertIn)

    # Test login and logout -> login, logout function
    def test_login_logout_valid_data(self):
        """Test routes for login and logout, correct data."""
        response = self.login('test@test.com', 'password')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('My account', response_data)
        self.assertIn('Logout', response_data)
        self.assertNotIn('Register', response_data)
        self.assertNotIn('Log In', response_data)
        self.assertIn('You were successfully logged in', response_data)

        # Log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertNotIn('My account', response_data)
        self.assertNotIn('Logout', response_data)
        self.assertIn('Register', response_data)
        self.assertIn('Log In', response_data)

    def test_login_invalid_data(self):
        """Test route for login."""
        login_data = [('test_new@test.com', 'password'), ('test@test.com', 'password_invalid')]
        for data_item in login_data:
            response = self.login(*data_item)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertNotIn('My account', response_data)
            self.assertNotIn('Logout', response_data)
            self.assertIn('Register', response_data)
            self.assertIn('Log In', response_data)
            if data_item[0] == 'test_new@test.com':
                self.assertIn('That email does not exist, please register.', response_data)
            else:
                self.assertIn('Password incorrect, please try again.', response_data)

    # Test registration -> register function
    def test_user_registration_valid_data(self):
        """Test route for registration, correct data."""
        response = self.register("Name", "Surname", "email@email.com", "password", "password", 1234)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('My account', response_data)
        self.assertIn('Logout', response_data)
        self.assertNotIn('Register', response_data)
        self.assertNotIn('Log In', response_data)

    def test_user_registration_invalid_data(self):
        """Test route for registration."""
        for data_item in register_invalid_data:
            response = self.client.post('/auth/register',
                                        data=data_item[0],
                                        follow_redirects=True
                                        )
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            if len(data_item[0]) <= 5:
                if data_item[1] != "password":
                    self.assertTrue(
                        re.search(f'id="{data_item[1]}" name="{data_item[1]}" required type="text" value=""',
                                  response_data))
                    self.assertIn('This field is required.', response_data)
                else:
                    self.assertTrue(
                        re.search(f'id="{data_item[1]}" name="{data_item[1]}" required type="password" value=""',
                                  response_data))
                    self.assertIn('This field is required.', response_data)
            else:
                if data_item[1] == "email_invalid":
                    self.assertIn('Invalid email address.', response_data)
                elif data_item[1] == "email_too_long":
                    self.assertIn('Invalid email address.', response_data)
                    self.assertIn('Field must be between 1 and 80 characters long.', response_data)
                elif data_item[1] == "email_exists":
                    self.assertIn('Email exists.', response_data)
                elif data_item[1] == "password":
                    self.assertIn('The passwords must be identical.', response_data)

    # Tests for routes with @admin_required decorator

    # Test users
    def test_users(self):
        """Test route for users, valid data."""
        self.login('admin@test.com', 'password')
        response = self.client.get(f'/auth/users', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('<th scope="row"> name</th>', response_data)
        self.assertIn('<td>test@test.com</td>', response_data)
        self.assertIn('<th scope="row"> moderator</th>', response_data)
        self.assertIn('<td>moderator@test.com</td>', response_data)
        self.assertIn('<th scope="row"> admin</th>', response_data)
        self.assertIn('<td>admin@test.com</td>', response_data)

    # Test show_user_reservations_admin
    def test_show_user_reservations_admin(self):
        """Test route for show_user_reservations_admin, valid data."""
        user_id = User.query.filter_by(email="test@test.com").first().id
        self.login('admin@test.com', 'password')
        response = self.client.get(f'/auth/user/{user_id}/reservations', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('There are no reservations', response_data)
        # Add reservation
        reservation = Rental(cars_id=1, users_id=user_id, from_date=datetime(2020, 5, 27),
                             to_date=datetime(2020, 5, 28),
                             available_from=datetime(2020, 5, 28, 1, 0, 0))
        db.session.add(reservation)
        db.session.commit()
        response = self.client.get(f'/auth/user/{user_id}/reservations', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('There are no reservations', response_data)
        self.assertIn('2020-05-27', response_data)
        self.assertIn('2020-05-28', response_data)

    def test_show_user_reservations_admin_invalid_data(self):
        """Test route for show_user_reservations_admin."""
        user_id = len(User.query.all()) + 1
        self.login('admin@test.com', 'password')
        response = self.client.get(f'/auth/user/{user_id}/reservations', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Page Not Found', response_data)

    # Test add_reservation
    def test_add_reservation(self):
        """Test route for add_reservation, valid data."""
        self.login('admin@test.com', 'password')
        user_id = User.query.filter_by(email="test@test.com").first().id
        # Add car
        car_dict = {"name": "Car_name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()

        car_id = random.choice(Car.query.all()).id
        from_date_time = (datetime.now() + timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
        to_date_time = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")
        response = self.client.post(f'/auth/user/reservations/add/user/{user_id}',
                                    data={"name": car_id,
                                          "from_date_time": from_date_time,
                                          "to_date_time": to_date_time},
                                    follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(Car.query.get(car_id).name, response_data)
        self.assertIn(from_date_time, response_data)
        self.assertIn(to_date_time, response_data)
        self.assertIn('Reservation added.', response_data)

    def test_add_reservation_invalid_data(self):
        """Test route for add_reservation"""
        self.login('admin@test.com', 'password')
        # Add car
        car_dict = {"name": "Car_name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()

        user_id = User.query.filter_by(email="test@test.com").first().id
        car_id = Car.query.filter_by(name="Car_name").first().id
        from_date_time = datetime.now() + timedelta(days=1)
        to_date_time = datetime.now() + timedelta(days=2)
        available_from = to_date_time + timedelta(hours=1)

        reservation_dict = {"cars_id": car_id, "users_id": user_id, "from_date": from_date_time,
                            "to_date": to_date_time, 'available_from': available_from}

        # Add reservation to db
        rental = Rental(**reservation_dict)
        db.session.add(rental)
        db.session.commit()

        # Test requests
        invalid_data = [({"from_date_time": change_date_to_str(to_date_time + timedelta(days=10)),
                          "to_date_time": change_date_to_str(to_date_time + timedelta(days=12))}, "name"),
                        ({"name": car_id, "to_date_time": change_date_to_str(to_date_time + timedelta(days=10))},
                         "required"),
                        ({"name": car_id, "from_date_time": change_date_to_str(to_date_time + timedelta(days=10))},
                         "required"),

                        ({"name": car_id, "from_date_time": change_date_to_str(to_date_time + timedelta(hours=20)),
                          "to_date_time": change_date_to_str(to_date_time + timedelta(hours=10))}, "Dates Error"),

                        ({"name": car_id, "from_date_time": change_date_to_str(from_date_time - timedelta(days=365)),
                          "to_date_time": change_date_to_str(to_date_time + timedelta(hours=10))}, "Datetime error."),

                        ({"name": car_id, "from_date_time": change_date_to_str(to_date_time - timedelta(hours=10)),
                          "to_date_time": change_date_to_str(to_date_time + timedelta(days=10))}, "Change dates",
                         "to_date"),
                        ({"name": car_id, "from_date_time": change_date_to_str(from_date_time - timedelta(hours=10)),
                          "to_date_time": change_date_to_str(from_date_time + timedelta(hours=10))}, "Change dates",
                         "from_date"),

                        ({"name": car_id, "from_date_time": change_date_to_str(from_date_time - timedelta(hours=10)),
                          "to_date_time": change_date_to_str(available_from + timedelta(minutes=10))}, "Change dates",
                         "dates")
                        ]
        for item in invalid_data:
            response = self.client.post(f'/auth/user/reservations/add/user/{user_id}',
                                        data=item[0],
                                        follow_redirects=True)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            if item[1] == "name":
                self.assertIn('Not a valid choice', response_data)
            elif item[1] == "required":
                self.assertIn('This field is required.', response_data)
            elif item[1] == "Dates Error":
                self.assertIn('Dates Error!', response_data)
            elif item[1] == "Datetime error.":
                self.assertIn(item[1], response_data)
            elif item[1] == "Change dates":
                self.assertIn("Change dates!", response_data)
                self.assertIn(
                    f'Available before: {(from_date_time - timedelta(minutes=61)).strftime("%Y-%m-%d %H:%M:%S")}',
                    response_data)
                self.assertIn(
                    f'Available after: {(available_from + timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S")}',
                    response_data)

    # Test delete_user_reservation
    def test_delete_user_reservation(self):
        """Test route for delete_user_reservation, valid data."""
        self.login('admin@test.com', 'password')
        # Add car
        car_dict = {"name": "Car_name", "price": 123, "year": 2000, "model": "Car model", "image": "car_image.jpg"}
        car = Car(**car_dict)
        db.session.add(car)
        db.session.commit()

        user_id = User.query.filter_by(email="test@test.com").first().id
        car_id = Car.query.filter_by(name="Car_name").first().id
        from_date_time = datetime.now() + timedelta(days=1)
        to_date_time = datetime.now() + timedelta(days=2)
        available_from = to_date_time + timedelta(hours=1)

        reservation_dict = {"cars_id": car_id, "users_id": user_id, "from_date": from_date_time,
                            "to_date": to_date_time, 'available_from': available_from}

        # Add reservation to db
        rental = Rental(**reservation_dict)
        db.session.add(rental)
        db.session.commit()

        # Test request
        response = self.client.post('/auth/user/reservations/delete',
                                    data={"car_id": car_id, "user_id": user_id, "from_date": from_date_time},
                                    follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Deleted", response_data)
        self.assertIn("There are no reservations", response_data)

    # Test edit_user_admin
    def test_edit_user_admin(self):
        """Test route for edit_user_admin, valid data."""
        user_id = User.query.filter_by(email="test@test.com").first().id
        self.login('admin@test.com', 'password')
        response = self.client.post(f'/auth/edit-user/{user_id}',
                                    data=dict(name="New name", surname='New surname', email='new_test@test.com',
                                              telephone="111", role=2),
                                    follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('The profile has been updated.', response_data)

        response = self.client.get(f'/auth/edit-user/{user_id}', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('required type="text" value="New name"', response_data)
        self.assertIn('required type="text" value="New surname"', response_data)
        self.assertIn('required type="text" value="new_test@test.com"', response_data)
        self.assertIn('<option selected value="2">Moderator', response_data)
        self.assertIn('required type="text" value="111"', response_data)
        self.assertIn('id="address" name="address" type="text" value=""', response_data)

    def test_edit_user_admin_invalid_data(self):
        """Test route for edit_user_admin."""
        user_id = len(User.query.all()) + 1
        self.login('admin@test.com', 'password')
        response = self.client.post(f'/auth/edit-user/{user_id}',
                                    data=dict(name="New name", surname='New surname', email='new_test@test.com',
                                              telephone="111", role=2),
                                    follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 404)
        self.assertIn('Page Not Found', response_data)

        # Invalid role id
        role_id = len(Role.query.all()) + 1
        user_id = User.query.filter_by(email="test@test.com").first().id
        response = self.client.post(f'/auth/edit-user/{user_id}',
                                    data={**register_invalid_data[0][0], "name": "name", "role": role_id},
                                    follow_redirects=True
                                    )
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Not a valid choice', response_data)

        # Invalid data
        user_id = User.query.filter_by(email="test@test.com").first().id
        for data_item in register_invalid_data:
            if data_item[1] != "password":
                response = self.client.post(f'/auth/edit-user/{user_id}',
                                            data={**data_item[0], "role": 1},
                                            follow_redirects=True
                                            )
                response_data = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                if len(data_item[0]) <= 5:
                    self.assertTrue(
                        re.search(f'id="{data_item[1]}" name="{data_item[1]}" required type="text"',
                                  response_data))
                    self.assertIn('This field is required.', response_data)
                else:
                    if data_item[1] == "email_invalid":
                        self.assertIn('Invalid email address.', response_data)
                    elif data_item[1] == "email_too_long":
                        self.assertIn('Invalid email address.', response_data)
                        self.assertIn('Field must be between 1 and 80 characters long.', response_data)

            if data_item[1] == "email_exists":
                data_item[0]["email"] = "admin@test.com"
                response = self.client.post(f'/auth/edit-user/{user_id}',
                                            data={**data_item[0], "role": 1},
                                            follow_redirects=True
                                            )
                response_data = response.get_data(as_text=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn('Email exists.', response_data)

    # Tests for functions without @admin_required

    # Test show_user
    def test_show_user(self):
        """Test route for show_user."""
        self.login('test@test.com', 'password')
        user = User.query.filter_by(email='test@test.com').first()

        # Test GET
        response = self.client.get('/auth/user', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'Hello {user.name}!', response_data)
        self.assertIn(user.email, response_data)
        self.assertIn("********", response_data)

        # Test POST
        user_data = [{"new_email": "test2@test.com", "password": "password", "submit_new_mail": "Save changes"},
                     {"old_password": "password", "new_password": "password2", "new_password_check": "password2",
                      "submit_new_password": "Save changes"}
                     ]
        for item in user_data:
            response = self.client.post('/auth/user', data={**item}, follow_redirects=True)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("Changes saved.", response_data)
            self.assertIn("test2@test.com", response_data)

        response = self.client.get('/auth/logout', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertNotIn("My account", response_data)
        response = self.login("test2@test.com", "password2")
        response_data = response.get_data(as_text=True)
        self.assertIn("My account", response_data)

    def test_show_user_invalid_data(self):
        """Test route for show_user, invalid data."""
        invalid_data = [
            ({"new_email": "test@test.com", "password": "password", "submit_new_mail": "Save changes"}, "email"),
            ({"new_email": "test@test.com", "password": "password2", "submit_new_mail": "Save changes"}, "password"),
            ({"old_password": "password2", "new_password": "password2", "new_password_check": "password2",
              "submit_new_password": "Save changes"}, "password")]
        self.login('test@test.com', 'password')
        for item in invalid_data:
            response = self.client.post('/auth/user', data={**item[0]}, follow_redirects=True)
            response_data = response.get_data(as_text=True)
            if item[1] == "email":
                self.assertIn("Email already exists.", response_data)
            else:
                self.assertIn("Wrong password", response_data)
            self.assertEqual(response.status_code, 200)

    # Test show_user_reservations
    def test_show_user_reservations(self):
        """Test route for show_user_reservations."""
        self.login('test@test.com', 'password')
        response = self.client.get('/auth/user/reservations')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("There are no reservations", response_data)

        # Add reservation
        user_id = User.query.filter_by(email="test@test.com").first().id
        from_date_time = datetime.now() + timedelta(days=1)
        to_date_time = datetime.now() + timedelta(days=2)
        available_from = to_date_time + timedelta(hours=1)
        reservation_dict = {"cars_id": 3, "users_id": user_id, "from_date": from_date_time, "to_date": to_date_time,
                            'available_from': available_from}
        rental = Rental(**reservation_dict)
        db.session.add(rental)
        db.session.commit()

        response = self.client.get('/auth/user/reservations')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(change_date_to_str(from_date_time), response_data)
        self.assertIn(change_date_to_str(to_date_time), response_data)

    # Test show_user_data
    def test_show_user_data(self):
        """Test route for show_user_data."""
        self.login('test@test.com', 'password')
        new_data = {"name": "name_new", "surname": "surname_new", "telephone": "321111", "address": "my_address"}
        response = self.client.post('/auth/user/data', data={**new_data}, follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Changes saved.", response_data)
        self.assertIn("name_new", response_data)
        self.assertIn("surname_new", response_data)
        self.assertIn("321111", response_data)
        self.assertIn("my_address", response_data)

    def test_show_user_data_invalid_data(self):
        """Test route for show_user_data, invalid data."""
        invalid_data = [
            {"name": "", "surname": "new_surname", "telephone": "1000000", "address": "my address"},
            {"name": "new_name", "surname": "", "telephone": "1000000", "address": "my address"},
            {"name": "new_name", "surname": "new_surname", "telephone": "", "address": "my address"}
        ]
        self.login('test@test.com', 'password')
        for item in invalid_data:
            response = self.client.post('/auth/user/data', data={**item}, follow_redirects=True)
            response_data = response.get_data(as_text=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn("This field is required.", response_data)
