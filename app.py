from flask import Flask, request, render_template, redirect, flash, session, jsonify, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from models import db, connect_db, User, Encounter
import random
from collections import Counter
import requests
import resources
import json
from forms import RegisterForm, LoginForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///lazy_wizard'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'secretsecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)

connect_db(app)
db.create_all()

@app.route('/')
def homepage():
    return render_template('home.html')


##User Routes


@app.route('/register', methods=['GET', 'POST'])
def handle_registration():
    if 'user_id' in session:
        flash('You are already logged in.', 'danger')
        return redirect('/')
    else:
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
                return redirect(f'/users/{user.username}')
            else:
                form.username.errors = ['Invalid Username/Password.']
        return render_template('login.html', form=form)

@app.route('/logout', methods=['POST'])
def handle_logout():
    """remove user_id from session"""
    session.pop('user_id')
    flash('Successfully logged out!', 'success')
    return redirect('/')

@app.route('/users/<username>')
def show_user_details(username):
    user = User.query.get_or_404(username)
    if user.username != session['user_id']:
        flash('Not authorized to do that.', 'danger')
        return redirect('/')
    else:
        return render_template('user_details.html', user=user)


##Encounter Routes


@app.route('/encounter')
def encounter_builder():
    """Show home page"""
    creature_types = resources.creature_types
    return render_template('encounter_builder.html', creature_types=creature_types)

@app.route('/encounter/calc-crs', methods=["POST"])
def calculate_crs():
    data = request.json
    difficulty = data['difficulty']
    density = data['density']

    crs = resources.convert_xp_to_cr(difficulty, density)
    counter = Counter()
    for cr in crs:
        counter[cr] += 1
    return jsonify(counter)


@app.route('/encounter/add-name', methods=['POST'])
def add_monster_name():
    data = request.json
    name = data['name']
    name.replace(' ','%20').capitalize()
    payload = {'name': str(name)}

    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    print(json)
    if json['results'] == []:
        err_dict = {'errors': {}}
        err_dict['errors']['invalid_name'] = "Couldn't find that monster."
        return jsonify(err_dict)
    else:   
        monster = json['results']
        return jsonify(monster)

@app.route('/encounter/search', methods=['POST'])
def add_monster_cr():
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
    print(json)
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
    data = request.json
    difficulty = data['difficulty']
    density = data['density']

    if difficulty == 0 :
        err_dict = {'errors': {}}
        err_dict['errors']['invalid_party'] = "You must create a party before generating an encounter."
        return jsonify(err_dict)
    else:
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
    data = request.json
    spells = {}

    for i, url in data.items():
        res = requests.get(url)
        spell = res.json()
        spells[f"{i}"] = spell
    
    return jsonify(spells)

@app.route('/encounter/create', methods=["POST"])
def save_encounter():
    title = request.form['title']
    monsters = json.loads(request.form['monsters'])
    username = session['user_id']
    new_encounter = Encounter(title=title, monsters=monsters, username=username)
    db.session.add(new_encounter)
    try:
        db.session.commit()
    except IntegrityError:
        flash('An encounter with that title already exists.', 'danger')
        return redirect(request.referrer)
    flash('Encounter saved!', 'success')
    return redirect(f'/users/{session["user_id"]}')

@app.route('/encounter/<int:encounter_id>', methods=['GET', 'POST'])
def show_encounter(encounter_id):
    if request.method == 'GET':
        encounter = Encounter.query.get_or_404(encounter_id)
        creature_types = resources.creature_types
        return render_template('encounter_details.html', encounter=encounter, creature_types=creature_types)
    else:
        encounter = Encounter.query.get_or_404(encounter_id)
        monsters = encounter.monsters
        return jsonify(monsters)

@app.route('/encounter/<int:encounter_id>/update', methods=['POST'])
def update_encounter(encounter_id):
    monsters = json.loads(request.form['monsters'])
    encounter = Encounter.query.get_or_404(encounter_id)
    encounter.monsters = monsters
    db.session.commit()
    flash('Encounter updated!', 'success')
    return redirect(f'/users/{session["user_id"]}')

@app.route('/encounter/<int:encounter_id>/delete', methods=['POST'])
def delete_encounter(encounter_id):
    encounter = Encounter.query.get_or_404(encounter_id)
    db.session.delete(encounter)
    db.session.commit()
    return redirect(f'/users/{session["user_id"]}')


## Route Functions


def get_next(json_response, results):
    if (json_response['next']):
        res = requests.get(f"{json_response['next']}")
        json = res.json()
        results += json['results']
        get_next(json, results)
