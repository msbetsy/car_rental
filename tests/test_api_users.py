"""This module stores tests for API - users module."""
import unittest
from app import create_app, db
from app.models import Role, User
from tests.api_functions import token, create_user, create_admin, create_moderator, check_missing_token_value, \
    check_permissions, check_missing_token_wrong_value, check_missing_token, request_with_features


def show_user_correct_request(client, user_id, api_headers):
    """Show user data request.

   :param client: Client of app
   :type client: flask.testing.FlaskClient
   :param user_id: Id of User
   :type user_id: int
   :param api_headers: Request headers
   :type api_headers: dict
   :return: Response for the request
   :rtype: flask.wrappers.Response
   """
    response = client.get(f'/api/v1/users/{user_id}/', headers=api_headers, follow_redirects=True)
    return response


def show_all_users_correct_request(client, api_headers):
    """Show all user data request.

       :param client: Client of app
       :type client: flask.testing.FlaskClient
       :param api_headers: Request headers
       :type api_headers: dict
       :return: Response for the request
       :rtype: flask.wrappers.Response
       """
    response = client.get('/api/v1/users/', headers=api_headers, follow_redirects=True)
    return response


class UsersTestCase(unittest.TestCase):
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
        self.user_moderator = create_moderator()
        self.token_moderator = token(self.client, self.user_moderator)
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

    def test_get_user(self):
        """Test api for get_user, correct data."""
        user_dict = {
            'email': 'user1@example.com', 'name': 'user1_name', 'surname': 'user1_surname', 'telephone': 123,
            'password': 'password', 'role_id': 1, 'address': None
        }
        user = User(**user_dict)
        db.session.add(user)
        db.session.commit()

        del user_dict['password']

        # Test request without features
        response = show_user_correct_request(self.client, user.id, self.get_api_headers_admin())
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        expected_result = {'success': True,
                           'data': {**user_dict,
                                    'id': 4,
                                    'post_number': 0,
                                    'posts': [],
                                    'rentals_number': 0,
                                    'rentals': [],
                                    'comments_number': 0,
                                    'comments': [],
                                    'opinions_number': 0,
                                    'opinions': []
                                    }}

        self.assertDictEqual(expected_result, response_data)

        # Test request with features: params
        response = self.client.get('/api/v1/users/{}/?params=comments,comments_number'.format(user.id),
                                   headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        expected_result = {'success': True,
                           'data': {**user_dict,
                                    'id': 4,
                                    'post_number': 0,
                                    'posts': [],
                                    'rentals_number': 0,
                                    'rentals': [],
                                    'opinions_number': 0,
                                    'opinions': []
                                    }}

        self.assertDictEqual(expected_result, response_data)

    def test_get_user_invalid_data(self):
        """Test api for get_user, correct data."""
        user_dict = {
            'email': 'user1@example.com', 'name': 'user1_name', 'surname': 'user1_surname', 'telephone': 123,
            'password': 'password', 'role_id': 1, 'address': None
        }
        user = User(**user_dict)
        db.session.add(user)
        db.session.commit()

        del user_dict['password']

        # Test request with features: params
        response = self.client.get('/api/v1/users/{}/?params=commentscomments_number'.format(user.id),
                                   headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        expected_result = {'success': True,
                           'data': {**user_dict,
                                    'id': 4,
                                    'post_number': 0,
                                    'posts': [],
                                    'rentals_number': 0,
                                    'rentals': [],
                                    'comments_number': 0,
                                    'comments': [],
                                    'opinions_number': 0,
                                    'opinions': []
                                    }}

        self.assertDictEqual(expected_result, response_data)

        # Test request with wrong user_id
        all_ids = [id_value.id for id_value in User.query.all()]
        user_id = max(all_ids) + 1
        response = show_user_correct_request(self.client, user_id, self.get_api_headers_admin())
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertFalse(response_data['success'])
        self.assertIn(str(user_id), response_data['error'], 'bad request')

    def test_get_all_users(self):
        """Test api for get_all_users with sorting, filtering records, correct data."""
        user_first_dict = {
            'email': 'user1@example.com', 'name': 'user1_name', 'surname': 'user1_surname', 'telephone': 123,
            'password': 'password', 'role_id': 1, 'address': None
        }
        user_first = User(**user_first_dict)
        user_second_dict = {
            'email': 'user2@example.com', 'name': 'user2_name', 'surname': 'user2_surname', 'telephone': 123,
            'password': 'password2', 'role_id': 2, 'address': None
        }
        user_second = User(**user_second_dict)
        db.session.add_all([user_first, user_second])
        db.session.commit()
        user_second.role_id = 2
        db.session.commit()

        user = self.user
        moderator = self.user_moderator
        admin = self.user_admin

        del user_first_dict['password']
        del user_second_dict['password']
        del user['password']
        del moderator['password']
        del admin['password']

        user['role_id'] = User.query.filter_by(email=self.user['email']).first().role_id
        moderator['role_id'] = User.query.filter_by(email=self.user_moderator['email']).first().role_id
        admin['role_id'] = User.query.filter_by(email=self.user_admin['email']).first().role_id

        user['address'] = None
        moderator['address'] = None
        admin['address'] = None

        # Test request without features
        response = self.client.get(request_with_features(url='/api/v1/users/'), headers=self.get_api_headers_admin(),
                                   follow_redirects=True)
        users_data = {
            'post_number': 0,
            'posts': [],
            'rentals_number': 0,
            'rentals': [],
            'comments_number': 0,
            'comments': [],
            'opinions_number': 0,
            'opinions': []
        }

        expected_result = {'success': True,
                           'number_of_records': 5,
                           'data': [
                               {**user, 'id': User.query.filter_by(email=self.user['email']).first().id, **users_data},
                               {**moderator, 'id': User.query.filter_by(email=self.user_moderator['email']).first().id,
                                **users_data},
                               {**admin, 'id': User.query.filter_by(email=self.user_admin['email']).first().id,
                                **users_data},
                               {**user_first_dict, 'id': 4, **users_data},
                               {**user_second_dict, 'id': 5, **users_data}
                           ]
                           }
        response_data = response.get_json()
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        response = self.client.get(request_with_features(
            url='/api/v1/users/', sort_by="-id",
            params="comments,comments_number,opinions,opinions_number,posts,post_number",
            filters="id[gte]=4&id[lte]=5"),
            headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')

        expected_result = {'success': True,
                           'number_of_records': 2,
                           'data': [
                               {**user_second_dict, 'id': 5, 'rentals': [], 'rentals_number': 0},
                               {**user_first_dict, 'id': 4, 'rentals': [], 'rentals_number': 0}
                           ]
                           }
        self.assertDictEqual(expected_result, response_data)


# Test permissions
def test_insufficient_permissions(self):
    """Test permissions."""
    # Check permissions for get_user
    user_id = User.query.filter_by(email='test@test.com').first().id
    api_headers = self.get_api_headers_admin()

    # Test user permissions
    api_headers['Authorization'] = f'Bearer {self.token}'
    response = show_user_correct_request(self.client, user_id, api_headers)
    check_permissions(response, self.assertEqual, self.assertFalse)

    # Test moderator permissions
    api_headers['Authorization'] = f'Bearer {self.token_moderator}'
    response = show_user_correct_request(self.client, user_id, api_headers)
    check_permissions(response, self.assertEqual, self.assertFalse)


# Testing decorators connected with values of request -> tokens
def test_missing_token_value(self):
    """Test if token has no value."""

    user_id = User.query.filter_by(email='test@test.com').first().id
    api_headers = self.get_api_headers_admin()
    api_headers['Authorization'] = 'Bearer'

    # Check get_user
    response = show_user_correct_request(self.client, user_id, api_headers)
    check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)


def test_missing_token_wrong_value(self):
    """Check if token has wrong value"""

    user_id = User.query.filter_by(email='test@test.com').first().id
    api_headers = self.get_api_headers_admin()
    api_headers['Authorization'] = 'Bearer token'

    # Check get_user
    response = show_user_correct_request(self.client, user_id, api_headers)
    check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)


def test_missing_token(self):
    """Check if token exists"""
    user_id = User.query.filter_by(email='test@test.com').first().id
    api_headers = self.get_api_headers_admin()
    del api_headers['Authorization']

    # Check get_user
    response = show_user_correct_request(self.client, user_id, api_headers)
    check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)
