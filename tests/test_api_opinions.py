"""This module stores tests for API - opinions module."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Role, Opinion, User
from tests.api_functions import token, create_user, check_missing_token_value, check_missing_token_wrong_value, \
    check_missing_token, request_with_features, check_content_type

opinions_data = [{'author_id': 1, 'text': 'My opinion.', 'image': 'opinion1.jpg', 'date': datetime(2020, 5, 17)},
                 {'author_id': 3, 'text': 'My text.', 'image': 'opinion3.jpg', 'date': datetime(2020, 5, 27)}]

opinions_invalid_data = [({"text": 34}, "text"), ({}, "text")]


def make_opinions():
    """Function that adds opinions to db."""
    for item in opinions_data:
        opinion = Opinion(**item)
        db.session.add(opinion)
        db.session.commit()


def change_dict_to_json(dict_name):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    changed_dict["author_url"] = "".join(('/api/v1/users/', str(changed_dict["author_id"]), "/"))
    changed_dict["image_url"] = "".join(('/static/img/', changed_dict["image"]))
    changed_dict["date"] = changed_dict["date"].strftime("%d/%m/%Y, %H:%M:%S")
    del changed_dict["image"]
    del changed_dict["author_id"]
    changed_dict["id"] = Opinion.query.filter_by(date=dict_name["date"]).first().id
    return changed_dict


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

    # Test show_opinions
    def test_show_opinions(self):
        """Test api for show_opinions with pagination, sorting, filtering records, correct data."""
        # Api headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features, no opinions
        # Request
        response = self.client.get('/api/v1/opinions/', headers=api_headers)
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'number_of_records': len(Opinion.query.all()),
                           'data': []}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Add opinions to db
        make_opinions()
        # Change dict to json format
        opinions = []
        for opinion in opinions_data:
            opinion = opinion.copy()
            opinions.append(change_dict_to_json(opinion))

        # Test request without features
        response = self.client.get('/api/v1/opinions/', headers=api_headers)
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'number_of_records': len(Opinion.query.all()),
                           'data': opinions}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        request_features = {'sort_by': '-id',
                            'params': 'date,author_url',
                            'filters': 'id[lt]=2'}
        response = self.client.get(
            request_with_features(url='/api/v1/opinions/', **request_features),
            headers=api_headers)
        response_data = response.get_json()

        # Expected results
        filtered_opinions = [item for item in opinions if item['id'] < 2]
        filtered_opinions_sorted = sorted(filtered_opinions, key=lambda item: item['id'], reverse=True)
        filtered_opinions_sorted_params = []

        for item in filtered_opinions_sorted:
            filtered_opinions_sorted_params.append(remove_params_from_dict(item, ["author_url", "date"]))

        expected_result = {'success': True,
                           'number_of_records': len(filtered_opinions_sorted_params),
                           'data': filtered_opinions_sorted_params}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test pagination
        request_features = {'per_page': '1',
                            'params': 'date,author_url'}
        response = self.client.get(
            request_with_features(url='/api/v1/opinions/', **request_features), headers=api_headers)
        response_data = response.get_json()
        # Expected results
        opinions_without_params = []
        for item in opinions:
            opinions_without_params.append(remove_params_from_dict(item, ["author_url", "date"]))
        expected_result = {'success': True,
                           'number_of_records': 1,
                           'data': [{**opinions_without_params[0]}],
                           'pagination': {
                               "current_page_url": "/api/v1/opinions/?page=1&params=date%2Cauthor_url&per_page=1",
                               "next_page": "/api/v1/opinions/?page=2&params=date%2Cauthor_url&per_page=1",
                               "number_of_all_pages": 2,
                               "number_of_all_records": 2
                           }}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test show_opinion
    def test_show_opinion(self):
        """Test api for show_opinion with filtering variables, correct data."""
        # Api headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features, no opinions
        # Request
        opinion_id = 1
        response = self.client.get(f'/api/v1/opinions/{opinion_id}/', headers=api_headers)
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': False,
                           'error': f'Opinion with id {opinion_id} not found',
                           }
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Add opinions to db
        make_opinions()
        # Change dict to json format
        opinions = []
        for opinion in opinions_data:
            opinion = opinion.copy()
            opinions.append(change_dict_to_json(opinion))

        # Test request without features
        # Request
        response = self.client.get(f'/api/v1/opinions/{opinion_id}/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        filtered_opinions = [item for item in opinions if item['id'] == opinion_id]
        expected_result = {'success': True,
                           'data': {**filtered_opinions[0]}
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        # Request
        request_features = {'params': 'author_url'}
        response = self.client.get(request_with_features(url=f'/api/v1/opinions/{opinion_id}/', **request_features),
                                   headers=api_headers)
        response_data = response.get_json()
        # Expected result
        filtered_opinions_without_params = []
        for item in filtered_opinions:
            filtered_opinions_without_params.append(remove_params_from_dict(item, ["author_url"]))
        expected_result = {'success': True,
                           'data': {**filtered_opinions_without_params[0]}
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_show_opinion_invalid_data(self):
        """Test api for show_opinion."""
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features
        response = self.client.get('/api/v1/opinions/opinion_name/', headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'not found')

    # Test add_opinion
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
        for opinion in opinions_invalid_data:
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
