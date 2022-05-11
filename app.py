from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User
import random
from collections import Counter
import requests
import resources
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///encgen'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretsecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()


@app.route('/')
def homepage():
    return redirect('/register')


##User Routes


@app.route('/register', methods=['GET', 'POST'])
def handle_registration():
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
        session['user_id'] = new_user.username
        flash ('Account created!', 'success')
        return redirect('/encounter')
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def handle_login():
    """Render and handle user login form"""
    if 'user_id' in session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            data = {k:v for k, v in form.data.items() if k != 'csrf_token'}
            user = User.authenticate(**data)

            if user:
                flash(f'Welcome back {user.username}!', 'success')
                session['user_id'] = user.username
                return redirect('/encounter')
            else:
                form.username.errors = ['Invalid Username/Password.']
        return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def handle_logout():
    """remove user_id from session"""
    session.pop('user_id')
    flash('Successfully logged out!', 'success')
    return redirect('/')


##Encounter Routes


@app.route('/encounter')
def home_page():
    """Show home page"""
    creature_types = resources.creature_types
    return render_template('encounter.html', creature_types=creature_types)

@app.route('/encounter/add-name', methods=['POST'])
def add_monster_name():
    data = request.json
    name = data['name']
    payload = {'name': str(name)}

    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    monster = json['results']
    return jsonify(monster)

@app.route('/encounter/add-cr', methods=['POST'])
def add_monster_cr():
    data = request.json
    cr = data['challenge_rating']
    payload = {'challenge_rating': str(cr)}

    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    results = json['results']
    get_next(json, results)
    monster = random.choice(results)
    return jsonify(monster)

@app.route('/encounter/create', methods=["POST"])
def generate_encounter():
    data = request.json
    difficulty = data['difficulty']
    density = data['density']
    type = data['type']

    crs = resources.convert_xp_to_cr(difficulty, density)
    counter = Counter()
    for cr in crs:
        counter[cr] += 1
    set_crs = set(crs)
    ordered = sorted(set_crs, reverse=True)
    monsters = {}

    for cr in ordered:
        payload = {}
        payload['challenge_rating'] = str(cr)
        if type != 'any':
             payload['type'] = type
        res = requests.get('https://api.open5e.com/monsters/', params=payload)
        json = res.json()
        results = json['results']
        get_next(json, results)
        monster = random.choice(results)
        monsters[f"{monster['name']}"] = {}
        monsters[f"{monster['name']}"]["count"] = counter[cr]
        monsters[f"{monster['name']}"]["data"] = monster

    return jsonify(monsters=monsters)

@app.route('/encounter/spells', methods=['POST'])
def get_spells():
    data = request.json
    spells = {}

    for i, url in data.items():
        res = requests.get(url)
        spell = res.json()
        spells[f"{i}"] = spell
    
    return jsonify(spells)

def get_next(json_response, results):
    if (json_response['next']):
        res = requests.get(f"{json_response['next']}")
        json = res.json()
        results += json['results']
        get_next(json, results)
