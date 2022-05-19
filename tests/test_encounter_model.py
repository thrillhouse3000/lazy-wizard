import os
from sqlalchemy import exc
from unittest import TestCase
from models import db, Encounter, User

os.environ['DATABASE_URL'] = "postgresql:///lazy_wizard_test"

from app import app

db.create_all()

class EncounterModelTestCase(TestCase):
    """Test model for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user = User.register("user1", "pwd", "user1@test.com")
    
        db.session.add(user)
        db.session.commit()

        user = User.query.get(user.username)

        self.user = user

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_encounter_model(self):
        """test basic encounter model"""

        e = Encounter(title='test', monsters='{"Test": "1"}', username=self.user.username)

        db.session.add(e)
        db.session.commit()

        self.assertEqual(len(self.user.encounters), 1)
        self.assertEqual(self.user.encounters[0].title, 'test')
    
    def test_badtitle_model(self):
        """test encounter title error handling"""

        e = Encounter(title=None, monsters='{"Test": "1"}', username=self.user.username)

        db.session.add(e)
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()


