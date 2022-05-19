import os
from unittest import TestCase
from models import db, User, Encounter

os.environ['DATABASE_URL'] = "postgresql:///lazy_wizard_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class UserRoutesTestCase(TestCase):
    """Test routes for users"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user = User.register("user", "pwd", "user@test.com")
        user2 = User.register("user2", "pwd", "user2@test.com")
        
        db.session.add(user)
        db.session.add(user2)
        db.session.commit()

        user = User.query.get(user.username)
        user2 = User.query.get(user2.username)

        self.user = user
        self.user2 = user2

        e = Encounter(title='test', monsters='{"Test": "1"}', username=self.user.username)
        db.session.add(e)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_details(self):
        """Check user details route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user.username
            res = c.get(f'/users/{self.user.username}')

            self.assertEqual(res.status_code, 200)
            self.assertIn("user\\\'s Profile", str(res.data))
            self.assertIn("test", str(res.data))
    
    

