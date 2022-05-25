from flask import Flask, request, render_template, redirect, flash, session, jsonify, g
import os
import requests
import json
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Encounter
from forms import RegisterForm, LoginForm
from collections import Counter
import random
import resources
from route_functions import already_logged_in, login_required, is_author, authorized_user, get_next

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = (os.environ.get('DATABASE_URL'.replace("://", "ql://", 1), 'postgresql:///lazy_wizard'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "keepitsecretkeepitsafe")
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

CURR_USER_KEY = 'curr-user'

@app.before_request
def add_user_to_g():
    """If logged in, add curr user to global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None

def set_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.username

def set_logout():
    """Logout user."""
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

##Routes

@app.route('/')
def homepage():
    """Render home page"""
    return render_template('home.html')

##User Routes

@app.route('/register', methods=['GET', 'POST'])
@already_logged_in
def handle_registration():
    """Render and handle user registration form"""
    form = RegisterForm()
    if form.validate_on_submit():
        data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
        new_user = User.register(**data)
        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username is already in use. Please choose a different one.')
            return render_template('register.html', form=form)
        set_login(new_user)
        flash ('Account created!', 'alert-success')
        return redirect(f'/users/{new_user.username}')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
@already_logged_in
def handle_login():
    """Render and handle user login form"""
    form = LoginForm()
    if form.validate_on_submit():
        data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
        user = User.authenticate(**data)
        if user:
            set_login(user)
            flash(f'Welcome back {user.username}!', 'alert-success')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid Username/Password.']
    return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def handle_logout():
    """Remove user from session"""
    set_logout()
    flash('Successfully logged out!', 'alert-success')
    return redirect('/')

@app.route('/users/<username>')
@login_required
@authorized_user
def show_user_details(username):
    """Render user's details"""
    user = User.query.get_or_404(username)
    return render_template('user_details.html', user=user)

##Encounter API Routes

@app.route('/encounter')
def encounter_builder():
    """Render the encounter building page"""
    creature_types = resources.creature_types
    return render_template('encounter_builder.html', creature_types=creature_types)

@app.route('/encounter/calc-crs', methods=["POST"])
def calculate_crs():
    """Return calculated CRs based on user inputs"""
    data = request.json
    xp_total = data['xp_total']
    density = data['density']

    crs = resources.convert_xp_to_cr(xp_total, density)
    counter = Counter()
    for cr in crs:
        counter[cr] += 1
    return jsonify(counter)

@app.route('/encounter/add-name', methods=['POST'])
def add_monster_name():
    """Get monster data based on name and return JSON"""
    data = request.json
    name = data['name']
    caps = [word.capitalize() for word in name.split(' ')]
    url_name = ' '.join(caps)
    payload = {'name': str(url_name)}
    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    if json['results'] == []:
        err_dict = {'errors': {}}
        err_dict['errors']['invalid_name'] = "Couldn't find that monster."
        return jsonify(err_dict)
    else:   
        monster = json['results']
        return jsonify(monster)

@app.route('/encounter/search', methods=['POST'])
def search_monster():
    """Retrieve list of monsters based off type and CR"""
    data = request.json
    cr = data['challenge_rating']
    type = data['type']

    if type == 'any':
        payload = {'challenge_rating': str(cr)}
    elif cr == '':
        payload = {'type': str(type)}
    else:
        payload = {'challenge_rating': str(cr), 'type': str(type)}

    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    if json['results'] == []:
        err_dict = {'errors': {}}
        err_dict['errors']['invalid_term'] = "No monsters of that type/CR found (CR must be between 0 and 30)."
        return jsonify(err_dict)
    else:   
        results = json['results']
        get_next(json, results)
        return jsonify(results)

@app.route('/encounter/generate', methods=["POST"])
def generate_encounter():
    """Create monster dictionary based off of calculated CRs. Return as JSON"""
    data = request.json
    xp_total = data['xp_total']
    density = data['density']

    if xp_total == 0 :
        err_dict = {'errors': {}}
        err_dict['errors']['invalid_party'] = "You must gather your party before venturing forth."
        return jsonify(err_dict)
    else:
        crs = resources.convert_xp_to_cr(xp_total, density)
        counter = Counter()
        for cr in crs:
            counter[cr] += 1
        set_crs = set(crs)
        ordered = sorted(set_crs, reverse=True)
        monsters = {}

        for cr in ordered:
            payload = {}
            payload['challenge_rating'] = str(cr)
            res = requests.get('https://api.open5e.com/monsters/', params=payload)
            json = res.json()
            results = json['results']
            get_next(json, results)
            monster = random.choice(results)
            monsters[f"{monster['slug']}"] = {}
            monsters[f"{monster['slug']}"]["count"] = counter[cr]
            monsters[f"{monster['slug']}"]["name"] = monster['name']
            monsters[f"{monster['slug']}"]["data"] = monster
        return jsonify(monsters=monsters)

@app.route('/encounter/spells', methods=['POST'])
def get_spells():
    """Fetch API data if monster has spell list"""
    data = request.json
    spells = {}

    for i, url in data.items():
        res = requests.get(url)
        spell = res.json()
        spells[f"{i}"] = spell
    return jsonify(spells)

#Encounter CRUD routes

@app.route('/encounter/create', methods=["POST"])
@login_required
def create_encounter():
    """Create encounter and upload to DB"""
    if request.form['monsters'] != '{}':
        try:
            title = request.form['title']
            monsters = request.form['monsters']
            monsters = json.loads(monsters)
            username = g.user.username
            new_encounter = Encounter(title=title, monsters=monsters, username=username)
            db.session.add(new_encounter)
        except ValueError:
            flash('Whoops, something went wrong. Try again!', 'alert-danger')
            return redirect(request.referrer)
    else:
        flash('Nothing to save.', 'alert-danger')
        return redirect(request.referrer)
    db.session.commit()
    flash('Encounter saved!', 'alert-success')
    return redirect(f'/users/{g.user.username}')

@app.route('/encounter/<int:encounter_id>', methods=['GET', 'POST'])
@login_required
@is_author
def show_encounter(encounter_id):
    """Render encounter template and retrieve encounter data"""
    encounter = Encounter.query.get_or_404(encounter_id)
    if request.method == 'GET':
        encounter = Encounter.query.get_or_404(encounter_id)
        creature_types = resources.creature_types
        return render_template('encounter_details.html', encounter=encounter, creature_types=creature_types)
    else:
        encounter = Encounter.query.get_or_404(encounter_id)
        monsters = encounter.monsters
        return jsonify(monsters)

@app.route('/encounter/<int:encounter_id>/update', methods=['POST'])
@login_required
@is_author
def update_encounter(encounter_id):
    """Update encounter in DB"""
    encounter = Encounter.query.get_or_404(encounter_id)
    monsters = json.loads(request.form['monsters'])
    encounter.monsters = monsters
    db.session.commit()
    flash('Encounter updated!', 'alert-success')
    return redirect(f'/users/{g.user.username}')

@app.route('/encounter/<int:encounter_id>/delete', methods=['POST'])
@login_required
@is_author
def delete_encounter(encounter_id):
    """Delete encounter from DB"""
    encounter = Encounter.query.get_or_404(encounter_id)
    db.session.delete(encounter)
    db.session.commit()
    return redirect(f'/users/{g.user.username}')



