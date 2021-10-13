"""This module stores tests for User model."""
import unittest
from app import create_app, db
from app.models import User, AnonymousUser, Role, Permission


class UserModelTestCase(unittest.TestCase):
    """Test User model."""

    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):
        """Check if password is hashed."""
        test_user = User(password='check_password')
        self.assertTrue(test_user.password_hash is not None)

    def test_no_password_getter(self):
        """Check if password has a getter function - not readable attribute"""
        test_user = User(password='check_password')
        with self.assertRaises(AttributeError):
            test_user.password

    def test_password_verification(self):
        """Check if process of password verification is correct."""
        test_user = User(password='check_password')
        self.assertTrue(test_user.verify_password('check_password'))
        self.assertFalse(test_user.verify_password('wrong_password'))

    def test_password_if_salts_are_random(self):
        """Check if salted password are random."""
        test_user1 = User(name="", surname="", email="john1@email.com", telephone="123", password='check_password')
        test_user2 = User(name="", surname="", email="john2@email.com", telephone="123", password='check_password')
        self.assertTrue(test_user1.password_hash != test_user2.password_hash)

    def test_user_role(self):
        """Check permissions of User (default role)."""
        u = User(email='john@mail.com', password='pass')
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
        self.assertFalse(u.is_admin())

    def test_moderator_role(self):
        """Check permissions of User (Moderator role)."""
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@mail.com', password='pass', role=r)
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
        self.assertFalse(u.is_admin())

    def test_administrator_role(self):
        """Check permissions of User (Administrator role)."""
        r = Role.query.filter_by(name='Administrator').first()
        u = User(email='john@mail.com', password='pass', role=r)
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))
        self.assertTrue(u.is_admin())

    def test_anonymous_user(self):
        """Check permissions of AnonymousUser."""
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
        self.assertFalse(u.is_admin())
