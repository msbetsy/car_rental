"""This module stores functions used for testing API."""
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
