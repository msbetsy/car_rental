"""This module stores basic tests of application."""
import unittest
import json
from flask import current_app
from app import create_app, db
from app.models import Role


class BasicsTestCase(unittest.TestCase):
    """Test the basics of the application."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):
        """Check if application exists."""
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        """Check if application is running in testing configuration."""
        self.assertTrue(current_app.config['TESTING'])

    def get_api_headers(self):
        """Method that returns response headers.

         :return: Headers
         :rtype: dict
         """

        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_404(self):
        """Check error when page not found."""
        response = self.client.get('/wrong/url', headers=self.get_api_headers())
        self.assertEqual(response.status_code, 404)
        json_response = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_response['error'], 'not found')
