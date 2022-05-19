import os
from unittest import TestCase
from models import db, User, Encounter

os.environ['DATABASE_URL'] = "postgresql:///lazy_wizard_test"

from app import app, CURR_USER_KEY

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class EncounterRouteTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.register("user1", "pwd", "user@test.com")
        user2 = User.register("user2", "pwd", "user2@test.com")
        
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        user1 = User.query.get(user1.username)
        user2 = User.query.get(user2.username)

        self.user1 = user1
        self.user2 = user2

        e = Encounter(title='test', monsters='{"Test": "1"}', username=self.user1.username)
        db.session.add(e)
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_calc_crs(self):
        """Test CR calculating route"""
        with self.client as c:
            res = c.post('/encounter/calc-crs', json={'xp_total': 700, 'density': 'one'})
            data = res.json

            self.assertEqual({'3': 1}, data)
    
    def test_add_by_name(self):
        """Test add by name route"""
        with self.client as c:
            res = c.post('/encounter/add-name', json={'name': 'cat'})
            data = res.json

            self.assertIn("Cat", str(data))

    def test_bad_add_by_name(self):
        """Test add by name error handling"""
        with self.client as c:
            res = c.post('/encounter/add-name', json={'name': 'sdhfskjdfhkjs'})
            data = res.json

            self.assertIn("Couldn't find that monster.", str(data))

    def test_search(self):
        """Test search route"""
        with self.client as c:
            res = c.post('/encounter/search', json={'challenge_rating': '3', 'type': 'beast'})
            data = res.json

            self.assertIn("'challenge_rating\': \'3\'", str(data))
            self.assertIn("'type\': \'beast\'", str(data))
    
    def test_encounter_create(self):
        """Test encounter creation"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.post('/encounter/create', data={'title': 'test2', 'monsters': '{"Test2": "2"}', 'username': 'user1'}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            e = Encounter.query.all()
            self.assertEqual(e[1].title, 'test2')