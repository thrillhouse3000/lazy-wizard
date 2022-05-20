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

        e = Encounter(title='test', monsters='{"Acolyte": "1"}', username=self.user1.username)
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

            self.assertIn("'challenge_rating': '3'", str(data))
            self.assertIn("'type': 'beast'", str(data))
    
    def test_bad_search(self):
        """Test search error handling"""
        with self.client as c:
            res = c.post('/encounter/search', json={'challenge_rating': '31', 'type': 'any'})
            data = res.json

            self.assertIn("No monsters of that type/CR found (CR must be between 0 and 30).", str(data))

    def test_generate(self):
        """Test generate route"""
        with self.client as c:
            res = c.post('/encounter/generate', json={'xp_total': 700, 'density': 'few'})
            data = res.json

            self.assertIn("'challenge_rating': '1'", str(data))
            self.assertIn("'count': 2", str(data))
    
    def test_bad_generate(self):
        """Test generate error handling"""
        with self.client as c:
            res = c.post('/encounter/generate', json={'xp_total': 0, 'density': 'few'})
            data = res.json

            self.assertIn("You must gather your party before venturing forth.", str(data))
    
    def test_spells(self):
        """Test spells route"""
        with self.client as c:
            res = c.post('/encounter/spells', json={'0': 'https://api.open5e.com/spells/light/'})
            data = res.json

            self.assertIn("'name': 'Light'", str(data))
    
    def test_encounter_create(self):
        """Test encounter creation"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.post('/encounter/create', data={'title': 'test2', 'monsters': '{"Test2": "2"}', 'username': 'user1'}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            e = Encounter.query.all()
            self.assertEqual(e[1].title, 'test2')
            self.assertEqual(len(e), 2)
    
    def test_no_session_create(self):
        """Test encounter create with no user in session"""
        with self.client as c:
            res = c.post('/encounter/create', data={'title': 'test2', 'monsters': '{"Test2": "2"}', 'username': 'user1'}, follow_redirects=True)
            
            self.assertEqual(res.status_code, 200)
            self.assertIn('Must be logged in to do that.', str(res.data))
            e = Encounter.query.all()
            self.assertEqual(len(e), 1)
    
    def test_encounter_details_get(self):
        """Test encounte details get route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.get('/encounter/1')

            self.assertEqual(res.status_code, 200)
            self.assertIn('<meta id="encounter-id" data-id="1">', str(res.data))
    
    def test_encounter_details_post(self):
        """Test encounter details get route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.post('/encounter/1')
            data = res.json

            self.assertEqual(res.status_code, 200)
            self.assertIn('Acolyte', data)
    
    def test_unauthorized_encounter_details(self):
        """Test unauthorized encounter details route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.username
            res = c.get('/encounter/1', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Not authorized to do that.', str(res.data))

    def test_encounter_update(self):
        """Test encounter update route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.post('/encounter/1/update', data={"monsters": '{"Cat": "1"}'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            e = Encounter.query.get_or_404(1)
            self.assertEqual(e.monsters, {"Cat": "1"})
    
    def test_unauthorized_update(self):
        """Test unauthorized update route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.username
            res = c.post('/encounter/1/update', data={"monsters": '{"Cat": "1"}'}, follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Not authorized to do that.', str(res.data))
            e = Encounter.query.get_or_404(1)
            self.assertEqual(e.monsters, '{"Acolyte": "1"}')
    
    def test_encounter_delete(self):
        """Test delete route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.username
            res = c.post('/encounter/1/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            e = Encounter.query.all()
            self.assertEqual(len(e), 0)
    
    def test_unauthorized_delete(self):
        """Test unauthorized delete route"""
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user2.username
            res = c.post('/encounter/1/delete', follow_redirects=True)

            self.assertEqual(res.status_code, 200)
            self.assertIn('Not authorized to do that.', str(res.data))
            e = Encounter.query.all()
            self.assertEqual(len(e), 1)