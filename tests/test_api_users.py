"""This module stores tests for API - users module."""
import unittest
from app import create_app, db
from app.models import Role, User
from tests.api_functions import token, create_user, create_admin, create_moderator


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
        self.user_admin = create_admin()
        self.token_admin = token(self.client, self.user_admin)
        self.user_moderator = create_moderator()
        self.token_moderator = token(self.client, self.user_moderator)

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

        response = self.client.get(
            '/api/v1/users/{}'.format(user.id),
            headers=self.get_api_headers_admin(), follow_redirects=True)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        del user_dict['password']
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
        response = self.client.get(
            '/api/v1/users/?sort=-id&params=comments,comments_number,opinions,opinions_number,posts,post_number&'
            'id[gte]=4&id[the]=5',
            headers=self.get_api_headers_admin(),
            follow_redirects=True)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        del user_first_dict['password']
        del user_second_dict['password']
        expected_result = {'success': True,
                           'number_of_records': 2,
                           'data': [
                               {**user_second_dict, 'id': 5, 'rentals': [], 'rentals_number': 0},
                               {**user_first_dict, 'id': 4, 'rentals': [], 'rentals_number': 0}
                           ]
                           }
        self.assertDictEqual(expected_result, response_data)
