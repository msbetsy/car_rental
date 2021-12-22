"""This module stores tests for API - users module."""
import unittest
from app import create_app, db
from app.models import Role, User, NewsPost, Rental, Opinion, Comment
from tests.api_functions import token, create_user, create_admin, create_moderator, check_missing_token_value, \
    check_permissions, check_missing_token_wrong_value, check_missing_token, request_with_features

users_data = [{'email': 'user1@example.com', 'name': 'user1_name', 'surname': 'user1_surname', 'telephone': 123,
               'password': 'password', 'role_id': 1, 'address': None},
              {'email': 'user2@example.com', 'name': 'user2_name', 'surname': 'user2_surname', 'telephone': 123,
               'password': 'password2', 'role_id': 2, 'address': None}
              ]


def make_users():
    """Function that adds users to db."""
    for item in users_data:
        user = User(**item)
        db.session.add(user)
        db.session.commit()
        if item["role_id"] != 1:
            user.role_id = item["role_id"]
            db.session.commit()


def change_dict_to_json(dict_name):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :return: Changed dict format
    :rtype: dict
    """
    if "address" not in dict_name:
        dict_name["address"] = None
    if 'role_id' not in dict_name:
        dict_name["role_id"] = User.query.filter_by(email=dict_name['email']).first().role_id
    dict_name["id"] = User.query.filter_by(email=dict_name['email']).first().id
    dict_name["posts"] = NewsPost.query.filter_by(author_id=dict_name["id"]).all()
    dict_name["post_number"] = len(dict_name["posts"])
    dict_name["opinions"] = Opinion.query.filter_by(author_id=dict_name["id"]).all()
    dict_name["opinions_number"] = len(dict_name["opinions"])
    dict_name["rentals"] = Rental.query.filter_by(users_id=dict_name["id"]).all()
    dict_name["rentals_number"] = len(dict_name["rentals"])
    dict_name["comments"] = Comment.query.filter_by(author_id=dict_name["id"]).all()
    dict_name["comments_number"] = len(dict_name["opinions"])
    del dict_name["password"]
    return dict_name


def remove_params_from_dict(dict_name, params=None):
    """Change dict to format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :param params: Parameters not displayed in response.
    :type params: list
    :return: Changed dict
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    if params is not None:
        for param in params:
            del changed_dict[param]
    return changed_dict


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
    """Test users module."""

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

    # Test get_user
    def test_get_user(self):
        """Test api for get_user, correct data."""
        user_id = 4
        # Test request without features, no users in db
        # Request
        response = show_user_correct_request(self.client, user_id, self.get_api_headers_admin())
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response_data['error'], f'User with id {user_id} not found')
        self.assertFalse(response_data['success'])

        # Add users to db
        make_users()

        # Change dict to json format
        users = [self.user, self.user_moderator, self.user_admin]
        for item in users_data:
            users.append(item.copy())
        for user in users:
            change_dict_to_json(user)
        users = sorted(users, key=lambda users_item: users_item['id'])

        # Test request without features
        # Request
        response = show_user_correct_request(self.client, user_id, self.get_api_headers_admin())
        response_data = response.get_json()
        # Expected result
        filtered_user = [item for item in users if item['id'] == user_id][0]
        expected_result = {'success': True,
                           'data': {**filtered_user}}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: params
        request_features = {'params': 'comments,comments_number'}
        response = self.client.get(request_with_features(f'/api/v1/users/{user_id}/', **request_features),
                                   headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'data': remove_params_from_dict(filtered_user, ["comments", "comments_number"])
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_get_user_invalid_data(self):
        """Test api for get_user."""
        # Test request without features
        response = self.client.get('/api/v1/users/user_id/', headers=self.get_api_headers_admin(),
                                   follow_redirects=True)
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'not found')

    # Test get_all_users
    def test_get_all_users(self):
        """Test api for get_all_users with sorting, filtering records, correct data."""
        # Add users to db
        make_users()
        # Change dict to json format
        users = [self.user, self.user_moderator, self.user_admin]
        for item in users_data:
            users.append(item.copy())
        for user in users:
            change_dict_to_json(user)
        users = sorted(users, key=lambda users_item: users_item['id'])

        # Test request without features
        response = self.client.get(request_with_features(url='/api/v1/users/'), headers=self.get_api_headers_admin(),
                                   follow_redirects=True)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'number_of_records': len(users),
                           'data': users
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        request_features = {'sort_by': '-id',
                            'per_page': '1',
                            'filters': 'id[gte]=4&id[lte]=5',
                            'params': 'comments,comments_number,opinions,opinions_number,posts,post_number'}
        response = self.client.get(request_with_features(url='/api/v1/users/', **request_features),
                                   headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        # Expected results
        filtered_users = [item for item in users if item['id'] == 4 or item['id'] == 5]
        filtered_users_sorted = sorted(filtered_users, key=lambda item: item['id'], reverse=True)
        filtered_users_sorted_without_params = []

        for item in filtered_users_sorted:
            filtered_users_sorted_without_params.append(
                remove_params_from_dict(item, ["comments", "comments_number", "opinions", "opinions_number", "posts",
                                               "post_number"]))
        expected_result = {
            'data': filtered_users_sorted_without_params[:1],
            'number_of_records': 1,
            'pagination': {
                'current_page_url': '/api/v1/users/?page=1&sort=-id&params=comments%2Ccomments_number%2C'
                                    'opinions%2Copinions_number%2Cposts%2Cpost_number&per_page=1&id%5B'
                                    'gte%5D=4&id%5Blte%5D=5',
                'next_page': '/api/v1/users/?page=2&sort=-id&params=comments%2Ccomments_number%2C'
                             'opinions%2Copinions_number%2Cposts%2Cpost_number&per_page=1&id%5Bgte%5D=4&'
                             'id%5Blte%5D=5',
                'number_of_all_pages': len(filtered_users_sorted_without_params),
                'number_of_all_records': len(filtered_users_sorted_without_params)},
            'success': True}

        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test permissions
    def test_insufficient_permissions(self):
        """Test permissions."""
        api_headers = self.get_api_headers_admin()

        # Check permissions for get_user
        user_id = User.query.filter_by(email='test@test.com').first().id

        # Test user permissions
        api_headers['Authorization'] = f'Bearer {self.token}'
        response = show_user_correct_request(self.client, user_id, api_headers)
        check_permissions(response, self.assertEqual, self.assertFalse)

        # Test moderator permissions
        api_headers['Authorization'] = f'Bearer {self.token_moderator}'
        response = show_user_correct_request(self.client, user_id, api_headers)
        check_permissions(response, self.assertEqual, self.assertFalse)

        # Check permissions for get_all_users

        # Test user permissions
        api_headers['Authorization'] = f'Bearer {self.token}'
        response = show_all_users_correct_request(self.client, api_headers)
        check_permissions(response, self.assertEqual, self.assertFalse)

        # Test moderator permissions
        api_headers['Authorization'] = f'Bearer {self.token_moderator}'
        response = show_all_users_correct_request(self.client, api_headers)
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

        # Check get_all_users
        response = show_all_users_correct_request(self.client, api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""

        user_id = User.query.filter_by(email='test@test.com').first().id
        api_headers = self.get_api_headers_admin()
        api_headers['Authorization'] = 'Bearer token'

        # Check get_user
        response = show_user_correct_request(self.client, user_id, api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check get_all_users
        response = show_all_users_correct_request(self.client, api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        user_id = User.query.filter_by(email='test@test.com').first().id
        api_headers = self.get_api_headers_admin()
        del api_headers['Authorization']

        # Check get_user
        response = show_user_correct_request(self.client, user_id, api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

        # Check get_all_users
        response = show_all_users_correct_request(self.client, api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)
