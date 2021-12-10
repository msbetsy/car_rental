"""This module stores tests for API - news_posts module."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Role, NewsPost, User
from tests.api_functions import token, create_user, create_moderator, check_missing_token_value, \
    check_missing_token_wrong_value, check_missing_token, request_with_features, check_content_type, check_permissions

post_data = [{"title": "first", "body": "one", "img_url": "one.img"},
             {"title": "second", "body": "two", "img_url": "two.img"}
             ]
post_invalid_data = [
    ({"title": "", "text": "one"}, "required", "title"),
    ({"title": "second", "text": ""}, "required", "text"),
    ({"title": "third", "text": "three", "image": "two.jpg"}, "value", "image"),
    ({"title": "third", "text": "three", "image": "two.pdf"}, "format", "image")
]


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
    if "img_url" in changed_dict:
        if '/static/img/' not in changed_dict["img_url"]:
            changed_dict["img_url"] = "".join(('/static/img/', changed_dict["img_url"]))
    else:
        changed_dict["img_url"] = "".join(('/static/img/', "no_img.jpg"))
    if 'date' not in changed_dict:
        changed_dict["date"] = datetime.now().strftime("%Y-%m-%d")
    if "body" in changed_dict:
        changed_dict["text"] = changed_dict["body"]
        del changed_dict["body"]
    if params is not None:
        for param in params:
            del changed_dict[param]
    return changed_dict


def make_posts(dates, authors):
    """Function that add posts to db.
    :param dates: Dates in string format
    :type dates: list
    :param authors: Author id
    :type authors: list"""
    item_number = 0
    for item in post_data:
        post = NewsPost(author_id=authors[item_number], date=dates[item_number], **item)
        db.session.add(post)
        db.session.commit()
        item_number += 1


class NewsPostsTestCase(unittest.TestCase):
    """Test news_posts module."""

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

    def get_api_headers_moderator(self):
        """Method that returns response headers for moderator.

         :return: Headers
         :rtype: dict
         """

        return {
            'Authorization': f'Bearer {self.token_moderator}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    # Test show_post
    def test_show_post(self):
        """Test api for show_post, valid data."""
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test when no posts
        response = self.client.get('/api/v1/posts/1/', headers=api_headers)
        response_data = response.get_json()
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertIn("1", response_data['error'])

        # Add posts to db
        dates = ["2020-10-01", "2020-11-01"]
        authors_id = [1, 2]
        make_posts(dates, authors_id)

        # Test request without features
        response = self.client.get('/api/v1/posts/1/', headers=api_headers)
        response_data = response.get_json()

        # Expected result
        all_posts_data = [post_data[0].copy(), post_data[1].copy()]
        all_posts_data[0]["date"] = dates[0]
        all_posts_data[1]["date"] = dates[1]
        news_dict = {'id': 1,
                     "comments_urls": [],
                     "comments_number": 0,
                     "user_url": '/api/v1/users/1/',
                     **change_dict_to_json(all_posts_data[0])}
        expected_result = {'success': True,
                           'data': news_dict
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test show_posts
    def test_show_posts(self):
        """Test api for show_posts."""
        # Add posts to db
        dates = ["2020-10-01", "2020-11-01"]
        authors_id = [1, 2]
        make_posts(dates, authors_id)

        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features
        response = self.client.get('/api/v1/posts/', headers=api_headers)
        response_data = response.get_json()

        # Expected result
        all_posts_data = [post_data[0].copy(), post_data[1].copy()]
        all_posts_data[0]["date"] = dates[0]
        all_posts_data[1]["date"] = dates[1]
        news_dict = [{'id': 1,
                      "comments_urls": [],
                      "comments_number": 0,
                      "user_url": '/api/v1/users/1/',
                      **change_dict_to_json(all_posts_data[0])},
                     {'id': 2,
                      "comments_urls": [],
                      "comments_number": 0,
                      "user_url": '/api/v1/users/2/',
                      **change_dict_to_json(all_posts_data[1])}
                     ]
        expected_result = {'success': True,
                           'number_of_records': 2,
                           'data': news_dict
                           }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: sort_by, params
        response = self.client.get(
            request_with_features(url='/api/v1/posts/', sort_by="-id",
                                  params="user_url,comments_number,comments_urls"),
            headers=api_headers)
        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': len(NewsPost.query.all()),
                           'data': [
                               {
                                   **change_dict_to_json(news_dict[1],
                                                         ["user_url", "comments_number", "comments_urls"])
                               },
                               {
                                   **change_dict_to_json(news_dict[0],
                                                         ["user_url", "comments_number", "comments_urls"])
                               }
                           ]}

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features: apply_filter, apply_args_filter, pagination
        response = self.client.get(
            request_with_features(url='/api/v1/posts/', sort_by="-id", per_page="1", filters="id[gte]=2",
                                  filer_values="comments_number=0"), headers=api_headers)

        response_data = response.get_json()
        expected_result = {'success': True,
                           'number_of_records': 1,
                           'data': [
                               {**change_dict_to_json(news_dict[1])}],
                           'pagination': {
                               'current_page_url':
                                   '/api/v1/posts/?page=1&sort=-id&per_page=1&id%5Bgte%5D=2&comments_number=0',
                               'number_of_all_pages': 1,
                               'number_of_all_records': 1}
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test add_post
    def test_add_post(self):
        """Test api for add_post, valid data."""
        post_json_data = {"title": "my title", "text": "my text"}
        response = self.client.post('/api/v1/posts/', json=post_json_data,
                                    headers=self.get_api_headers_moderator())
        response_data = response.get_json()

        # Expected result
        author_id = User.query.filter_by(email="moderator@test.com").first().id
        expected_result = {'success': True,
                           'data': {'id': 1,
                                    "comments_urls": [],
                                    "comments_number": 0,
                                    "user_url": f'/api/v1/users/{author_id}/',
                                    **change_dict_to_json(post_json_data)}
                           }
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_post_invalid_data(self):
        """Test api for add_post, invalid data."""
        for post in post_invalid_data:
            response = self.client.post('/api/v1/posts/', json=post[0],
                                        headers=self.get_api_headers_moderator())
            response_data = response.get_json()

            # Expected result
            author_id = User.query.filter_by(email="moderator@test.com").first().id
            expected_result = {'success': True,
                               'data': {'id': 1,
                                        "comments_urls": [],
                                        "comments_number": 0,
                                        "user_url": f'/api/v1/users/{author_id}/',
                                        **change_dict_to_json(post[0])}
                               }
            # Tests
            if post[1] == "required":
                self.assertEqual(response_data['error']['message'], f"{post[2]} can't be null")
            elif post[1] == "format":
                self.assertEqual(response_data['error']['message'],
                                 'Wrong value, must be whole path , wrong format of file.')
            else:
                self.assertEqual(response_data['error']['message'],
                                 f"Unable to copy file. [Errno 2] No such file or directory: '{post[0]['image']}'")

            self.assertEqual(response.status_code, 400)
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error']['error'], 'bad request')
            self.assertEqual(response_data['error_value_key'], post[2])

    # Testing methods connected with values of request (content-type, tokens)
    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers_moderator()
        del api_headers['Content-Type']

        # Check add_post
        response = self.client.post('/api/v1/posts/', data=post_data[0], headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers_moderator()
        api_headers['Authorization'] = 'Bearer'

        # Check add_post
        response = self.client.post('/api/v1/posts/', json=post_data[0], headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers_moderator()
        api_headers['Authorization'] = 'Bearer token'

        # Check add_post
        response = self.client.post('/api/v1/posts/', json=post_data[0], headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check add_post
        response = self.client.post('/api/v1/posts/', json=post_data[0], headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    # Test permissions
    def test_insufficient_permissions(self):
        """Test permissions."""

        # Check permissions for add_post
        response = self.client.post('/api/v1/posts/', json=post_data[0], headers=self.get_api_headers())
        check_permissions(response, self.assertEqual, self.assertFalse)
