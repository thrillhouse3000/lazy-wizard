import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User

os.environ['DATABASE_URL'] = "postgresql:///lazy_wizard_test"

from app import app

db.create_all()

class UserModelTestCase(TestCase):
    def setUp(self):
        db.drop_all()
        db.create_all()

        user1 = User.register("user1", "pwd", "user1@test.com")

        db.session.add(user1)
        db.session.commit()

        user1 = User.query.get(user1.username)

        self.user1 = user1

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Test basic user model"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        self.assertEqual(len(u.encounters), 0)
    
    def test_register(self):
        """test register method"""
        u = User.register('test', 'password', 'test@test.test')
        db.session.add(u)
        db.session.commit()

        test_user = User.query.get(u.username)
        self.assertIsNotNone(test_user)
        self.assertEqual(test_user.username, 'test')
        self.assertEqual(test_user.email, 'test@test.test')
        self.assertNotEqual(test_user.password, 'password')
    
    def test_badusername_register(self):
        """test register username error handling"""
        u = User.register(None, 'password', 'test@test.test')
        db.session.add(u)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_duplicateusername_register(self):
        """test register duplicate username error handling"""
        u = User.register('user1', 'password', 'test@test.test')
        db.session.add(u)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_bademail_register(self):
        """test register email error handling"""
        u = User.register('test', 'password', None)
        db.session.add(u)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_badpassword_signup(self):
        """test register password error handling"""
        with self.assertRaises(ValueError) as context:
            User.register('test', '', 'test@test.test')
        with self.assertRaises(ValueError) as context:
            User.register('test', None, 'test@test.test')

    def test_auth(self):
        """test authenticate method"""
        u = User.authenticate(self.user1.username, 'pwd')
        self.assertTrue(u)
        self.assertEqual(u.username, 'user1')

    def test_badusername_auth(self):
        """test authentincate usernae error handling"""
        self.assertFalse(User.authenticate('badbad', 'pwd'))
    
    def test_badpassword_auth(self):
        """test authentincate password error handling"""
        self.assertFalse(User.authenticate(self.user1.username, 'badpwd'))