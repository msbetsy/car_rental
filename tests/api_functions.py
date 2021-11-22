"""This module stores functions used for testing API."""
import unittest
import flask.testing


def token(client, test_user):
    """Create jwt token.

    :param client: Client of app
    :type client: flask.testing.FlaskClient
    :param test_user: User of app - data
    :type test_user: dict
    :return: jwt token
    :rtype: str
    """
    response = client.post('/api/v1/auth/login/', json={
        'email': test_user['email'],
        'password': test_user['password']
    })
    return response.get_json()['token']


def user(client):
    """Register user.

    :param client: Client of app
    :type client: flask.testing.FlaskClient
    :return: User data
    :rtype: dict
    """
    test_user = {
        'name': 'name',
        'surname': 'surname',
        'telephone': 12345,
        'password': 'password',
        'email': 'test@test.com'
    }

    client.post('/api/v1/auth/register/', json=test_user)
    return test_user


def admin(client):
    """Register admin.

    :param client: Client of app -> admin
    :type client: flask.testing.FlaskClient
    :return: Admin data
    :rtype: dict
    """
    admin_user = {
        'name': 'admin',
        'surname': 'admin',
        'telephone': 12345,
        'password': 'password',
        'email': 'admin@test.com',
        'role_id': 3
    }

    client.post('/api/v1/auth/register/', json=admin_user)
    return admin_user


def check_content_type(response: flask.wrappers.Response, check_equal, check_false):
    """Function for testing content type.

    :param response: The response for request
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_false: Method that checks if the values is false
    :type check_false: unittest.TestCase
    """
    response_data = response.get_json()
    check_equal(response.status_code, 415)
    check_equal(response.headers['Content-Type'], 'application/json')
    check_equal(response_data['error'], 'unsupported media type')
    check_equal(response_data['message'], 'Content type must be: application/json')
    check_false(response_data['success'])


def check_missing_token(response: flask.wrappers.Response, check_equal, check_false, check_not_in):
    """Function for testing missing token.

    :param response: The response for request
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_false: Method that checks if the values is false
    :type check_false: unittest.TestCase
    :param check_not_in: Method that checks if the values is not in container
    :type check_not_in: unittest.TestCase
    """
    response_data = response.get_json()
    check_equal(response.status_code, 400)
    check_false(response_data['success'])
    check_not_in('data', response_data)
    check_equal(response_data['error'], 'bad request')
    check_equal(response_data['message'], 'No Authorization token')


def check_missing_token_value(response: flask.wrappers.Response, check_equal, check_false, check_not_in):
    """Function for testing missing token value.

    :param response: The response for request
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_false: Method that checks if the values is false
    :type check_false: unittest.TestCase
    :param check_not_in: Method that checks if the values is not in container
    :type check_not_in: unittest.TestCase
    """
    response_data = response.get_json()
    check_equal(response.status_code, 400)
    check_false(response_data['success'])
    check_not_in('data', response_data)
    check_equal(response_data['error'], 'bad request')
    check_equal(response_data['message'], 'No token, log in or register')


def check_missing_token_wrong_value(response: flask.wrappers.Response, check_equal, check_false, check_not_in):
    """Function for testing wrong token value.

    :param response: The response for request
    :param check_equal: Method that checks if the values are equal
    :type check_equal: unittest.TestCase
    :param check_false: Method that checks if the values is false
    :type check_false: unittest.TestCase
    :param check_not_in: Method that checks if the values is not in container
    :type check_not_in: unittest.TestCase
    """
    response_data = response.get_json()
    check_equal(response.status_code, 401)
    check_false(response_data['success'])
    check_not_in('data', response_data)
    check_equal(response_data['error'], 'unauthorized')
    check_equal(response_data['message'], 'Invalid token. Please login or register')
