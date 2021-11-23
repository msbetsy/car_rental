"""This module stores tests for API - authentication module."""
import unittest
from app import create_app, db
from app.models import Role, User
from tests.api_functions import token, create_user, create_admin, check_content_type, check_missing_token, \
    check_missing_token_value, check_missing_token_wrong_value


def register():
    """Function that contains possible registration data - all cases are wrong.

    :return: Registration cases
    :rtype: list
    """
    registration_data = [
        ({'name': 'name', 'surname': 'surname', 'password': '123456', 'telephone': 1234}, 'email'),
        ({'surname': 'surname', 'password': '123456', 'email': 'e@test.com', 'telephone': 1234}, 'name'),
        ({'name': 'name', 'password': '123456', 'email': 'e@test.com', 'telephone': 1234}, 'surname'),
        ({'name': 'name', 'surname': 'surname', 'email': 'e@test.com', 'telephone': 1234}, 'password'),
        ({'name': 'name', 'surname': 'surname', 'password': '123456', 'email': 'e@test.com'}, 'telephone'),
        ({'name': 'name', 'surname': 'surname', 'password': '123456',
          'email': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@test.com',
          'telephone': 1234}, 'email'),
        ({'name': 'name', 'surname': 'surname', 'password': '123456',
          'email': 'ee.test.com',
          'telephone': 1234}, 'email')
    ]
    return registration_data


def login():
    """Function that contains possible login data - all cases are wrong.

     :return: Login cases
     :rtype: list
     """
    login_data = [
        ({'password': '123456'}, 'email'),
        ({'email': 'e@test.com'}, 'password'),
        ({'password': '123456', 'email': 'test@test.com'}, 'credentials'),
        ({'password': '123456', 'email': 'e@test.com'}, 'credentials')
    ]
    return login_data


def update_credentials():
    """Function that contains possible update credentials data - all cases are wrong.

     :return: Update cases
     :rtype: list
     """
    update_credentials_data = [
        ({'email': 'test@test.com', 'new_email': 'test2@test.com'}, 'no_password'),
        ({'password': '123456', 'email': 'test@test.com'}, 'new_password, new_email'),
        ({'email': 'test@test.com', 'new_email': 'test2@test.com', 'password': '1234'}, 'password'),
        ({'new_email': 'test@test.com', 'password': 'password'}, 'new_email')
    ]
    return update_credentials_data


def update_data():
    """Function that contains possible update data - all cases are wrong.

    :return: Update cases
    :rtype: list
    """
    data = [
        ({'name': 'name', 'surname': 'surname', 'email': 'test@test.com', 'password': '123456', 'telephone': 1234},
         'email'),
        ({'name': 'name', 'surname': 'surname', 'email': 'test2@test.com', 'telephone': 1234},
         'no_password'),
        ({'name': 'name', 'surname': 'surname', 'email': 'test2@test.com', 'password': 'password22', 'telephone': 1234},
         'wrong_password'),
        ({'name': 'name', 'email': 'test2@test.com', 'password': 'password22', 'new_password': '123'},
         'password'),
        ({'name': 'name', 'surname': 'surname', 'password': 'password',
          'email': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@test.com',
          'telephone': 1234}, 'long_email'),
        ({'name': 'name', 'surname': 'surname', 'password': 'password',
          'email': 'ee.test.com',
          'telephone': 1234}, 'wrong_email')
    ]
    return data


def update_data_by_admin():
    """Function that contains possible update data by admin - all cases are wrong.

    :return: Update cases
    :rtype: list
    """
    user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
    data = [
        ({'name': 'name', 'surname': 'surname', 'email': 'test@test.com'}, 'no_user_to_edit_id'),
        ({'name': 'name', 'surname': 'surname', 'email': 'test2@test.com', 'telephone': 1234, 'user_to_edit_id': 1.4},
         'user_to_edit_id'),
        ({'name': 'name', 'surname': 'surname', 'role_id': 4, 'user_to_edit_id': user_to_edit_id},
         'role_id'),
        ({'name': 'name', 'email': 'test@test.com', 'password': 'password22', 'new_password': '123',
          'user_to_edit_id': user_to_edit_id}, 'email'),
        ({'name': 'name', 'surname': 'surname', 'user_to_edit_id': user_to_edit_id,
          'email': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee@test.com',
          'telephone': 1234}, 'long_email'),
        ({'name': 'name', 'surname': 'surname', 'user_to_edit_id': user_to_edit_id,
          'email': 'ee.test.com',
          'telephone': 1234}, 'wrong_email')
    ]
    return data


def update_user_correct_request(client, api_headers):
    """Send request for update user data.

   :param client: Client of app
   :type client: flask.testing.FlaskClient
   :param api_headers: Request headers
   :type api_headers: dict
   :return: Response for the request
   :rtype: flask.wrappers.Response
   """
    response = client.put('/api/v1/auth/user/',
                          json={
                              'name': 'New_name',
                              'surname': 'New_surname',
                              'telephone': 9876,
                              'new_password': 'new_password',
                              'email': 'test2@test.com',
                              'password': 'password'
                          },
                          headers=api_headers, follow_redirects=True)
    return response


def update_user_by_admin_correct_request(client, api_headers_admin, user_to_edit_id):
    """Send request for update user by admin.

   :param client: Client of app
   :type client: flask.testing.FlaskClient
   :param api_headers_admin: Request headers for admin
   :type api_headers_admin: dict
   :param user_to_edit_id: Id of editing user
   :type user_to_edit_id: int
   :return: Response for the request
   :rtype: flask.wrappers.Response
   """
    response = client.put('/api/v1/auth/admin/',
                          json={
                              'user_to_edit_id': user_to_edit_id,
                              'name': 'New_name2',
                              'role_id': 2
                          },
                          headers=api_headers_admin, follow_redirects=True)
    return response


def update_user_credentials_correct_request(client, api_headers):
    """Send request for update user credentials.

   :param client: Client of app
   :type client: flask.testing.FlaskClient
   :param api_headers: Request headers
   :type api_headers: dict
   :return: Response for the request
   :rtype: flask.wrappers.Response
   """
    response = client.patch('/api/v1/auth/user/',
                            json={
                                'password': 'password',
                                'email': 'test2@test.com',
                                'new_password': 'password2'
                            },
                            headers=api_headers, follow_redirects=True)
    return response


class AuthenticationTestCase(unittest.TestCase):
    """Test authentication module."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()
        self.user = create_user()
        self.token = token(self.client, self.user)
        self.user_admin = create_admin()
        self.token_admin = token(self.client, self.user_admin)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self):
        """Method that returns response headers.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def get_api_headers_admin(self):
        """Method that returns response headers for admin.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token_admin}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    # Testing methods connected with admin
    def test_update_user_by_admin(self):
        """Test api for update user by admin, correct data."""
        user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
        surname = User.query.get(user_to_edit_id).surname
        address = User.query.get(user_to_edit_id).address
        email = User.query.get(user_to_edit_id).email
        telephone = User.query.get(user_to_edit_id).telephone
        api_headers = self.get_api_headers_admin()
        response = update_user_by_admin_correct_request(self.client, api_headers, user_to_edit_id)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['name'], 'New_name2')
        self.assertEqual(response_data['role'], 'Moderator')
        self.assertEqual(surname, User.query.get(user_to_edit_id).surname)
        self.assertEqual(address, User.query.get(user_to_edit_id).address)
        self.assertEqual(email, User.query.get(user_to_edit_id).email)
        self.assertEqual(telephone, User.query.get(user_to_edit_id).telephone)

    def test_update_user_by_admin_invalid_data(self):
        """Test api for update user by admin, incorrect data."""
        api_headers = self.get_api_headers_admin()
        for item in update_data_by_admin():
            response = self.client.put('/api/v1/auth/admin/', json=item[0], headers=api_headers,
                                       follow_redirects=True)
            response_data = response.get_json()
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            if item[1] == 'no_user_to_edit_id':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'No user_to_edit_id')
            elif item[1] == 'user_to_edit_id':
                self.assertEqual(response.status_code, 404)
                self.assertIn(str(item[0]['user_to_edit_id']), response_data['error'])
            elif item[1] == 'role_id':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'Wrong role_id')
            elif item[1] == 'email':
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response_data['error'], 'conflict')
                self.assertIn(item[0]['email'], response_data['message'])
            else:
                if len(item[0]['email']) > 80:
                    self.assertEqual(response_data['error']['error'], 'bad request')
                    self.assertEqual(response_data['error_value_key'], 'email')
                    self.assertEqual(response_data['error']['message'], 'Maximum number of characters is 80.')
                else:
                    self.assertEqual(response_data['error']['error'], 'bad request')
                    self.assertEqual(response_data['error_value_key'], 'email')
                    self.assertEqual(response_data['error']['message'], 'Email is incorrect.')

    # Testing methods connected with registration
    def test_registration(self):
        """Test api for registration, correct data."""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']
        response = self.client.post('/api/v1/auth/register/',
                                    json={
                                        'name': 'test',
                                        'surname': 'test',
                                        'password': 'password',
                                        'email': 'test@email.com',
                                        'telephone': '123456789'
                                    }, headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['token'])

    def test_registration_already_used_email(self):
        """Test api for registration, incorrect data - email is in db."""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']
        response = self.client.post('/api/v1/auth/register/',
                                    json={
                                        'name': 'test',
                                        'surname': 'test',
                                        'password': 'password',
                                        'email': 'test@test.com',
                                        'telephone': '123456789'
                                    }, headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response_data['error'], 'conflict')
        self.assertEqual(response_data['message'], 'User with email test@test.com already exists')
        self.assertFalse(response_data['success'])

    def test_registration_invalid_data(self):
        """Test api for registration, incorrect data."""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']
        for item in register():
            response = self.client.post('/api/v1/auth/register/',
                                        json=item[0], headers=api_headers)
            response_data = response.get_json()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            self.assertNotIn('token', response_data)
            all_mandatory_data = True
            mandatory_data = ['name', 'surname', 'telephone', 'password', 'email']
            for key in mandatory_data:
                if key not in item[0].keys():
                    all_mandatory_data = False
                    break
            if item[1] == 'email' and all_mandatory_data is False:
                self.assertEqual(response_data['error'], 'bad request')
            elif item[1] == 'email':
                self.assertEqual(item[1], response_data['error_value_key'])
                if len(item[0]['email']) > 80:
                    self.assertEqual(response_data['error']['message'], 'Maximum number of characters is 80.')
                else:
                    self.assertEqual(response_data['error']['message'], 'Email is incorrect.')
            else:
                self.assertEqual(item[1], response_data['error_value_key'])
                self.assertIn(item[1], response_data['error']['message'])

    # Testing methods connected with login
    def test_login(self):
        """Test api for login, correct data."""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']
        response = self.client.post('/api/v1/auth/login/',
                                    json={
                                        'password': 'password',
                                        'email': 'test@test.com'
                                    }, headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['token'])

    def test_login_invalid_data(self):
        """Test api for registration, incorrect data."""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']
        for item in login():
            response = self.client.post('/api/v1/auth/login/',
                                        json=item[0], headers=api_headers)
            response_data = response.get_json()
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            self.assertNotIn('token', response_data)
            if item[1] == 'email':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'No email')
            elif item[1] == 'password':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'No password')
            else:
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response_data['error'], 'unauthorized')
                self.assertEqual(response_data['message'], 'Invalid credentials')

    # Testing methods connected with current user
    def test_get_current_user(self):
        """Test api for current user."""
        response = self.client.get('/api/v1/auth/about_me/',
                                   headers=self.get_api_headers())
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['name'], self.user['name'])
        self.assertEqual(response_data['data']['surname'], self.user['surname'])
        self.assertEqual(response_data['data']['email'], self.user['email'])
        self.assertEqual(response_data['data']['telephone'], self.user['telephone'])
        self.assertEqual(response_data['data']['address'], None)
        self.assertNotIn('id', response_data['data'])
        self.assertNotIn('role_id', response_data['data'])
        self.assertNotIn('posts', response_data['data'])
        self.assertNotIn('post_number', response_data['data'])
        self.assertNotIn('rentals_number', response_data['data'])
        self.assertNotIn('rentals', response_data['data'])
        self.assertNotIn('comments_number', response_data['data'])
        self.assertNotIn('comments', response_data['data'])
        self.assertNotIn('opinions_number', response_data['data'])
        self.assertNotIn('opinions', response_data['data'])

    # Testing methods connected with updating data
    def test_update_user_data(self):
        """Test api for updating user, correct data.."""
        response = update_user_correct_request(self.client, self.get_api_headers())
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])
        self.assertEqual(response_data['data']['name'], 'New_name')
        self.assertEqual(response_data['data']['surname'], 'New_surname')
        self.assertEqual(response_data['data']['telephone'], 9876)
        self.assertEqual(response_data['data']['email'], 'test2@test.com')

    def test_update_user_invalid_data(self):
        """Test api for updating user, incorrect data.."""
        for item in update_data():
            response = self.client.put('/api/v1/auth/user/', json=item[0], headers=self.get_api_headers(),
                                       follow_redirects=True)
            response_data = response.get_json()
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            if item[1] == 'email':
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response_data['error'], 'conflict')
                self.assertIn(item[0]['email'], response_data['message'])
            elif item[1] == 'no_password':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], "No password, can't update email")
            elif item[1] == 'wrong_password':
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response_data['error'], 'unauthorized')
                self.assertEqual(response_data['message'], 'Invalid credentials, wrong password')
            elif item[1] == 'password':
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response_data['error'], 'unauthorized')
                self.assertEqual(response_data['message'], 'Invalid credentials, wrong password')
            else:
                if len(item[0]['email']) > 80:
                    self.assertEqual(response_data['error']['error'], 'bad request')
                    self.assertEqual(response_data['error_value_key'], 'email')
                    self.assertEqual(response_data['error']['message'], 'Maximum number of characters is 80.')
                else:
                    self.assertEqual(response_data['error']['error'], 'bad request')
                    self.assertEqual(response_data['error_value_key'], 'email')
                    self.assertEqual(response_data['error']['message'], 'Email is incorrect.')

    def test_update_credentials(self):
        """Test api for update credentials, correct data."""
        response = update_user_credentials_correct_request(self.client, self.get_api_headers())
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data['success'])

    def test_update_credentials_invalid_data(self):
        """Test api for update credentials, incorrect data."""
        for item in update_credentials():
            response = self.client.patch('/api/v1/auth/user/',
                                         json=item[0], headers=self.get_api_headers())
            response_data = response.get_json()
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            if item[1] == 'no_password':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'No password')
            elif item[1] == 'new_password, new_email':
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response_data['error'], 'bad request')
                self.assertEqual(response_data['message'], 'No new data')
            elif item[1] == 'password':
                self.assertEqual(response.status_code, 401)
                self.assertEqual(response_data['error'], 'unauthorized')
                self.assertEqual(response_data['message'], 'Invalid password')
            else:
                self.assertEqual(response.status_code, 409)
                self.assertEqual(response_data['error'], 'conflict')
                self.assertIn(item[0]['new_email'], response_data['message'])

    # Testing methods connected with values of request (content-type, tokens)
    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer'

        # Check About me
        response = self.client.get('/api/v1/auth/about_me/', headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for PATCH (change credentials)
        update_user_credentials_correct_request(self.client, api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data (PUT)
        response = update_user_correct_request(self.client, api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data by admin (PUT)
        user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
        api_headers_admin = self.get_api_headers_admin()
        api_headers_admin['Authorization'] = 'Bearer'
        response = update_user_by_admin_correct_request(self.client, api_headers_admin, user_to_edit_id)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer token'

        # Check About me
        response = self.client.get('/api/v1/auth/about_me/', headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for PATCH (change credentials)
        update_user_credentials_correct_request(self.client, api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data (PUT)
        response = update_user_correct_request(self.client, api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data by admin (PUT)
        user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
        api_headers_admin = self.get_api_headers_admin()
        api_headers_admin['Authorization'] = 'Bearer token'
        response = update_user_by_admin_correct_request(self.client, api_headers_admin, user_to_edit_id)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check About user
        response = self.client.get('/api/v1/auth/about_me/', headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for PATCH (change credentials)
        update_user_credentials_correct_request(self.client, api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data (PUT)
        response = update_user_correct_request(self.client, api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check for update user data by admin (PUT)
        user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
        api_headers_admin = self.get_api_headers_admin()
        del api_headers_admin['Authorization']
        response = update_user_by_admin_correct_request(self.client, api_headers_admin, user_to_edit_id)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers()

        # Check for PATCH (change credentials)
        del api_headers['Content-Type']
        response = self.client.patch('/api/v1/auth/user/',
                                     data={
                                         'password': 'password',
                                         'email': 'test2@test.com',
                                         'new_password': 'password2'
                                     },
                                     headers=api_headers, follow_redirects=True)
        check_content_type(response, self.assertEqual, self.assertFalse)

        # Check for update user data (PUT)
        response = self.client.put('/api/v1/auth/user/',
                                   data={
                                       'name': 'New_name',
                                       'surname': 'New_surname',
                                       'telephone': 9876,
                                       'new_password': 'new_password',
                                       'email': 'test2@test.com',
                                       'password': 'password'
                                   },
                                   headers=api_headers, follow_redirects=True)
        check_content_type(response, self.assertEqual, self.assertFalse)

        # Check for POST (login)
        response = self.client.post('/api/v1/auth/login/',
                                    data={
                                        'password': 'password',
                                        'email': 'test@test.com'
                                    }, headers=api_headers, follow_redirects=True)
        check_content_type(response, self.assertEqual, self.assertFalse)

        # Check for POST (registration)
        response = self.client.post('/api/v1/auth/register/',
                                    data={
                                        'username': 'test',
                                        'password': 'password',
                                        'email': 'test@email.com'
                                    }, headers=api_headers, follow_redirects=True)
        check_content_type(response, self.assertEqual, self.assertFalse)

        # Check for update user data by admin (PUT)
        user_to_edit_id = User.query.filter_by(email='test@test.com').first().id
        api_headers_admin = self.get_api_headers_admin()
        del api_headers_admin['Content-Type']
        response = self.client.put('/api/v1/auth/admin/',
                                   data={
                                       'user_to_edit_id': user_to_edit_id,
                                       'name': 'New_name2'
                                   },
                                   headers=api_headers_admin, follow_redirects=True)
        check_content_type(response, self.assertEqual, self.assertFalse)
