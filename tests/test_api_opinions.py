"""This module stores tests for API - opinions module."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Role, Opinion, User
from tests.api_functions import token, create_user, check_missing_token_value, check_missing_token_wrong_value, \
    check_missing_token, request_with_features, check_content_type


def change_dict_to_json(dict_name, params=None):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :param params: Parameters not displayed in response.
    :type params: list
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    changed_dict["author_url"] = "".join(('/api/v1/users/', str(changed_dict["author_id"]), "/"))
    changed_dict["image_url"] = "".join(('/static/img/', changed_dict["image"]))
    changed_dict["date"] = changed_dict["date"].strftime("%d/%m/%Y, %H:%M:%S")
    del changed_dict["image"]
    del changed_dict["author_id"]
    if params is not None:
        for param in params:
            del changed_dict[param]
    return changed_dict


def make_opinion():
    """Function that contains possible opinion data - all cases are wrong.

     :return: opinion
     :rtype: list
     """
    opinion_data = [
        ({"text": 34}, "text"),
        ({}, "text")
    ]
    return opinion_data


class OpinionsTestCase(unittest.TestCase):
    """Test opinions module."""

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

    def test_show_opinions(self):
        """Test api for show_opinions with pagination, sorting, filtering records, correct data."""
        opinion_first_dict = {'author_id': 1, 'text': 'My opinion.', 'image': 'opinion1.jpg',
                              'date': datetime(2020, 5, 17)}
        opinion_second_dict = {'author_id': 3, 'text': 'My text.', 'image': 'opinion3.jpg',
                               'date': datetime(2020, 5, 27)}
        opinion_first = Opinion(**opinion_first_dict)
        opinion_second = Opinion(**opinion_second_dict)
        db.session.add_all([opinion_first, opinion_second])
        db.session.commit()

        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features
        response = self.client.get('/api/v1/opinions/', headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': 2,
                           'data': [
                               {'id': 1, **change_dict_to_json(opinion_first_dict)},
                               {'id': 2, **change_dict_to_json(opinion_second_dict)}
                           ]}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        response = self.client.get(
            request_with_features(url='/api/v1/opinions/', sort_by="-id", params="date,author_url", filters="id[lt]=2"),
            headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': 1,
                           'data': [
                               {'id': 1, **change_dict_to_json(opinion_first_dict, ["author_url", "date"])}
                           ]}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test pagination
        response = self.client.get(
            request_with_features(url='/api/v1/opinions/', per_page="1", params="date,author_url"), headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': 1,
                           'data': [
                               {'id': 1, **change_dict_to_json(opinion_first_dict, ["author_url", "date"])}
                           ],
                           'pagination': {
                               "current_page_url": "/api/v1/opinions/?page=1&params=date%2Cauthor_url&per_page=1",
                               "next_page": "/api/v1/opinions/?page=2&params=date%2Cauthor_url&per_page=1",
                               "number_of_all_pages": 2,
                               "number_of_all_records": 2
                           }}
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_show_opinion(self):
        """Test api for show_opinion with filtering variables, correct data."""
        opinion_dict = {'author_id': 1, 'text': 'My opinion.', 'image': 'opinion1.jpg', 'date': datetime(2020, 5, 17)}
        opinion = Opinion(**opinion_dict)
        db.session.add(opinion)
        db.session.commit()

        api_headers = self.get_api_headers()
        del api_headers["Authorization"]
        # Test request without features
        response = self.client.get('/api/v1/opinions/1/', headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data': {'id': 1, **change_dict_to_json(opinion_dict)}
                           }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        response = self.client.get(request_with_features(url='/api/v1/opinions/1/', params="author_url"),
                                   headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'data': {'id': 1, **change_dict_to_json(opinion_dict, ["author_url"])}
                           }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_show_opinion_invalid_data(self):
        """Test api for show_opinion."""

        api_headers = self.get_api_headers()
        del api_headers["Authorization"]
        # Test request without features
        response = self.client.get('/api/v1/opinions/1/', headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertIn("1", response_data['error'])

    def test_add_opinion(self):
        """Test api for add_opinion, correct data."""
        response = self.client.post('/api/v1/opinions/',
                                    json={"text": "test opinion"},
                                    headers=self.get_api_headers())
        response_data = response.get_json()
        user_id = User.query.filter_by(email='test@test.com').first().id
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data['data']['text'], "test opinion")
        self.assertEqual(response_data['data']['id'], 1)
        self.assertEqual(response_data['data']['author_url'], '/api/v1/users/{}/'.format(user_id))
        self.assertIn(datetime.today().strftime("%d/%m/%Y"), response_data['data']['date'])
        self.assertIn('/static/img/opinion', response_data['data']['image_url'])

    def test_add_opinion_invalid_data(self):
        """Test api for add_opinion."""
        for opinion in make_opinion():
            response = self.client.post('/api/v1/opinions/',
                                        json=opinion[0],
                                        headers=self.get_api_headers())
            response_data = response.get_json()
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error_value_key'], opinion[1])
            self.assertEqual(response_data['error']['error'], 'bad request')

    # Testing methods connected with values of request (content-type, tokens)
    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers()

        # Check add_opinion
        del api_headers['Content-Type']
        response = self.client.post('/api/v1/opinions/', data={"text": "Opinion"}, headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer'

        # Check add_opinion
        response = self.client.post('/api/v1/opinions/', json={"text": "Opinion"}, headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer token'

        # Check add_opinion
        response = self.client.post('/api/v1/opinions/', json={"text": "Opinion"}, headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check add_opinion
        response = self.client.post('/api/v1/opinions/', json={"text": "Opinion"}, headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)
