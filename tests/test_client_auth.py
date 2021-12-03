"""This module stores tests for client app.auth routes."""
import unittest
import re
from app import create_app, db
from app.models import Role
from tests.api_functions import create_user, create_admin, create_moderator


def check_login_required_must_login(client_with_http_method, url, check_equal, check_in):
    """Function for testing wrong token value.

    :param client_with_http_method: Client of app with HTTP method
    :type client_with_http_method: flask.testing.FlaskClient
    :param url: The route
    :type url: str
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_in: Method that checks if the values is not in container
    :type check_in: unittest.TestCase
    """
    response = client_with_http_method(url, follow_redirects=True)
    response_data = response.get_data(as_text=True)
    check_equal(response.status_code, 200)
    check_in('Please log in to access this page.', response_data)


def check_admin_required(client_with_http_method, url, check_equal, check_in, check_not_in):
    """Function for testing wrong token value.

    :param client_with_http_method: Client of app with HTTP method
    :type client_with_http_method: flask.testing.FlaskClient
    :param url: The route
    :type url: str
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_not_in: Method that checks if the values is not in container
    :type check_not_in: unittest.TestCase
    """
    response = client_with_http_method(url, follow_redirects=True)
    check_equal(response.status_code, 403)
    response_data = response.get_data(as_text=True)
    check_in("Forbidden", response_data)
    check_not_in("Name", response_data)
    check_not_in("Email", response_data)


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
        for response in responses:
            # Test users function from app.auth.views
            check_admin_required(self.client.get, '/auth/users', self.assertEqual, self.assertIn, self.assertNotIn)
            # Test edit_user_admin function from app.auth.views
            check_admin_required(self.client.get, f'/auth/edit-user/{user_id}', self.assertEqual, self.assertIn,
                                 self.assertNotIn)
            # Test show_user_reservations_admin function from app.auth.views
            check_admin_required(self.client.get, f'/auth/user/{user_id}/reservations', self.assertEqual, self.assertIn,
                                 self.assertNotIn)
            # Test add_reservation function from app.auth.views
            check_admin_required(self.client.get, f'/auth/user/reservations/add/user/{user_id}', self.assertEqual,
                                 self.assertIn, self.assertNotIn)
            # Test delete_user_reservation function from app.auth.views
            check_admin_required(self.client.get, '/auth/user/reservations/delete', self.assertEqual, self.assertIn,
                                 self.assertNotIn)

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
