"""This module stores basic tests of application."""
import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    """Test the basics of the application."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

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
