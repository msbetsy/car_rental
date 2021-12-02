"""This module stores tests for client app.auth routes."""
import unittest
from app import create_app, db
from app.models import Role
from tests.api_functions import token, create_user


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
        self.token = token(self.client, self.user)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

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

    def test_login_logout_valid_data(self):
        """Test routes for login and logout, correct data."""
        response = self.login('test@test.com', 'password')
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('My account', response_data)
        self.assertIn('Logout', response_data)
        self.assertNotIn('Register', response_data)
        self.assertNotIn('Log In', response_data)

        # Log out
        response = self.client.get('/auth/logout', follow_redirects=True)
        response_data = response.get_data(as_text=True)
        self.assertNotIn('My account', response_data)
        self.assertNotIn('Logout', response_data)
        self.assertIn('Register', response_data)
        self.assertIn('Log In', response_data)

    def test_user_registration_valid_data(self):
        """Test route for registration, correct data."""
        response = self.register("Name", "Surname", "email@email.com", "password", "password", 1234)
        response_data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('My account', response_data)
        self.assertIn('Logout', response_data)
        self.assertNotIn('Register', response_data)
        self.assertNotIn('Log In', response_data)
