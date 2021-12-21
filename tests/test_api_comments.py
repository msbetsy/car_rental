"""This module stores tests for API - comments module."""
import unittest
from datetime import datetime
from app import create_app, db
from app.models import Role, Comment, NewsPost
from tests.api_functions import token, create_user, check_missing_token_value, check_missing_token_wrong_value, \
    check_missing_token, request_with_features, check_content_type

comments_data = [{"post_id": 2, "author_id": 1, "text": "New one", "date": datetime(2020, 6, 30),
                  "parent_comment": 2},
                 {"post_id": 1, "author_id": 2, "text": "New comment", "date": datetime(2020, 5, 27),
                  "parent_comment": 0}]
comments_invalid_data = [
    ({"post_id": 2, "author_id": 1, "text": "New", "parent_comment": 0, "upper_comment": 0}, "post"),
    ({"author_id": 1, "text": "New", "parent_comment": 0, "upper_comment": 0}, "post_id"),
    ({"post_id": 1, "author_id": 1, "text": 123, "parent_comment": "9", "upper_comment": 0}, "text"),
    ({"post_id": 1, "author_id": 1, "parent_comment": "9", "upper_comment": 0}, "text"),
    ({"post_id": 1, "author_id": 1, "text": "New", "parent_comment": 0, "upper_comment": "5"}, "upper_comment"),
    ({"post_id": 1, "author_id": 1, "text": "New", "parent_comment": 0}, "upper_comment"),
    ({"post_id": 0, "author_id": 1, "text": "New", "parent_comment": 0, "upper_comment": 0}, "post"),
    ({"post_id": 1, "author_id": 1, "text": "New", "parent_comment": 0, "upper_comment": -1}, "upper_comment")
]


def make_comments():
    """Function that adds comments to db."""
    for item in comments_data:
        comment = Comment(**item)
        db.session.add(comment)
        db.session.commit()


def change_dict_to_json(dict_name):
    """Change dict to json format matching the response.

    :param dict_name: Name of the dictionary.
    :type dict_name: dict
    :return: Changed dict format
    :rtype: dict
    """
    changed_dict = dict_name.copy()
    if changed_dict["parent_comment"] != 0:
        changed_dict["upper_comment_url"] = "".join(('/api/v1/comments/', str(changed_dict["parent_comment"]), "/"))
    else:
        changed_dict["upper_comment_url"] = None

    changed_dict["author_url"] = "".join(('/api/v1/users/', str(changed_dict["author_id"]), "/"))
    changed_dict["post_url"] = "".join(('/api/v1/posts/', str(changed_dict["post_id"]), "/"))

    if "date" in changed_dict:
        changed_dict["id"] = Comment.query.filter_by(post_id=dict_name["post_id"], author_id=dict_name["author_id"],
                                                     parent_comment=changed_dict["parent_comment"],
                                                     date=changed_dict["date"]).first().id
        changed_dict["date"] = changed_dict["date"].strftime("%d/%m/%Y, %H:%M:%S")
    else:
        changed_dict["id"] = Comment.query.filter_by(post_id=dict_name["post_id"], author_id=dict_name["author_id"],
                                                     parent_comment=changed_dict["parent_comment"],
                                                     date=datetime.today()).first().id
        changed_dict["date"] = datetime.today().strftime("%d/%m/%Y, %H:%M:%S")

    del changed_dict["parent_comment"]
    del changed_dict["author_id"]
    del changed_dict["post_id"]
    if 'upper_comment' in changed_dict:
        del changed_dict['upper_comment']
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


class CommentsTestCase(unittest.TestCase):
    """Test comments module."""

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

    # Test show_comment
    def test_show_comment(self):
        """Test api for show_comment with filtering variables, correct data."""
        comment_id = 1
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features, no comments in db
        # Request
        response = self.client.get(f'/api/v1/comments/{comment_id}/', headers=api_headers)
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response_data['error'], f'Comment with id {comment_id} not found')
        self.assertFalse(response_data['success'])

        # Add comments to db
        make_comments()
        # Change dict to json format
        comments = []
        for comment in comments_data:
            comment = comment.copy()
            comments.append(change_dict_to_json(comment))

        # Test request without features
        # Request
        response = self.client.get(f'/api/v1/comments/{comment_id}/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'data': [item for item in comments if item['id'] == comment_id][0]
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        # Request
        request_features = {'params': 'author_url,upper_comment_url'}
        response = self.client.get(
            request_with_features(url=f'/api/v1/comments/{comment_id}/', **request_features), headers=api_headers)
        response_data = response.get_json()
        # Expected result
        comments_params = []
        for item in comments:
            comments_params.append(remove_params_from_dict(item, ["author_url", "upper_comment_url"]))

        expected_result = {'success': True,
                           'data': comments_params[0]}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_show_comment_invalid_data(self):
        """Test api for show_comments."""
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features
        # Request
        response = self.client.get('/api/v1/comments/comment_id/', headers=api_headers)
        response_data = response.get_json()
        # Tests
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['error'], 'not found')

    # Test show_comments
    def test_show_comments(self):
        """Test api for show_comments with pagination, sorting, filtering records, correct data."""
        # Headers
        api_headers = self.get_api_headers()
        del api_headers["Authorization"]

        # Test request without features, no comments
        # Request
        response = self.client.get('/api/v1/comments/', headers=api_headers)
        response_data = response.get_json()
        # Expected results
        expected_result = {'success': True,
                           'number_of_records': len(Comment.query.all()),
                           'data': []}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Add comments
        make_comments()
        # Change dict to json format
        comments = []
        for comment in comments_data:
            comment = comment.copy()
            comments.append(change_dict_to_json(comment))

        # Test request without features
        # Request
        response = self.client.get('/api/v1/comments/', headers=api_headers)
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'number_of_records': len(Comment.query.all()),
                           'data': comments
                           }
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test request with features
        # Request
        request_features = {'sort_by': 'date',
                            'params': 'author_url,post_url,upper_comment_url'}
        response = self.client.get(
            request_with_features(url='/api/v1/comments/', **request_features), headers=api_headers)
        response_data = response.get_json()
        # Expected result
        sorted_comments = sorted(comments, key=lambda comments_item: comments_item['date'])
        sorted_comments_params = []
        for item in sorted_comments:
            sorted_comments_params.append(
                remove_params_from_dict(item, ["author_url", "post_url", "upper_comment_url"]))

        expected_result = {'success': True,
                           'number_of_records': len(sorted_comments_params),
                           'data': sorted_comments_params}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

        # Test pagination
        # Request
        request_features = {'per_page': '1',
                            'filters': 'id[lt]=2',
                            'params': 'author_url,post_url,upper_comment_url'}
        response = self.client.get(request_with_features(url='/api/v1/comments/', **request_features),
                                   headers=api_headers)
        response_data = response.get_json()
        # Expected result
        filtered_comments = [item for item in comments if item['id'] < 2]
        filtered_comments_params = []
        for item in filtered_comments:
            filtered_comments_params.append(
                remove_params_from_dict(item, ["author_url", "post_url", "upper_comment_url"]))

        expected_result = {'success': True,
                           'number_of_records': len(filtered_comments_params),
                           'data': filtered_comments_params,
                           'pagination': {
                               "current_page_url": "/api/v1/comments/?page=1&params=author_url%2Cpost_url%2Cupper_"
                                                   "comment_url&per_page=1&id%5Blt%5D=2",
                               "number_of_all_pages": len(filtered_comments_params),
                               "number_of_all_records": len(filtered_comments_params)
                           }}
        # Tests
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    # Test add_comment
    def test_add_comment(self):
        """Test api for add_comment."""
        comment_dict = {"post_id": 1, "author_id": 1, "text": "New comment", "parent_comment": 0, "upper_comment": 0}
        # Add NewsPost to db
        post = NewsPost(author_id=3, title="Post", date=datetime(2020, 5, 25), body="Body of post", img_url="image.jpg")
        db.session.add(post)
        db.session.commit()
        # Request
        response = self.client.post(f'/api/v1/comments/', json=comment_dict, headers=self.get_api_headers())
        response_data = response.get_json()
        # Expected result
        expected_result = {'success': True,
                           'data': {**change_dict_to_json(comment_dict)}
                           }
        # Tests
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertDictEqual(expected_result, response_data)

    def test_add_comment_invalid_data(self):
        """Test api for add_comment."""
        # Add NewsPost to db
        post = NewsPost(author_id=3, title="Post", date=datetime(2020, 5, 25), body="Body of post", img_url="image.jpg")
        db.session.add(post)
        db.session.commit()
        # Requests with tests
        for comment in comments_invalid_data:
            # Request
            response = self.client.post('/api/v1/comments/', json=comment[0], headers=self.get_api_headers())
            response_data = response.get_json()
            # Tests
            self.assertEqual(response.status_code, 400)
            self.assertFalse(response_data['success'])
            self.assertEqual(response_data['error_value_key'], comment[1])

    # Testing methods connected with values of request (content-type, tokens)
    def test_invalid_content_type(self):
        """Check if content type is 'application/json'"""
        api_headers = self.get_api_headers()

        # Check add_opinion
        del api_headers['Content-Type']
        response = self.client.post('/api/v1/comments/', data={"text": "Comment"}, headers=api_headers)
        check_content_type(response, self.assertEqual, self.assertFalse)

    def test_missing_token_value(self):
        """Test if token has no value."""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer'

        # Check add_opinion
        response = self.client.post('/api/v1/comments/', json={"text": "Comment"}, headers=api_headers)
        check_missing_token_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token_wrong_value(self):
        """Check if token has wrong value"""
        api_headers = self.get_api_headers()
        api_headers['Authorization'] = 'Bearer token'

        # Check add_opinion
        response = self.client.post('/api/v1/comments/', json={"text": "Comment"}, headers=api_headers)
        check_missing_token_wrong_value(response, self.assertEqual, self.assertFalse, self.assertNotIn)

    def test_missing_token(self):
        """Check if token exists"""
        api_headers = self.get_api_headers()
        del api_headers['Authorization']

        # Check add_opinion
        response = self.client.post('/api/v1/comments/', json={"text": "Comment"}, headers=api_headers)
        check_missing_token(response, self.assertEqual, self.assertFalse, self.assertNotIn)
