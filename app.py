from flask import Flask, request, render_template, redirect, flash, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db
import random
import requests
import resources
# from forms import

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
def home_page():
    """Show home page"""
    creature_types = resources.creature_types
    terrain_types = resources.terrain_types
    return render_template('encounter.html', creature_types=creature_types, terrain_types=terrain_types)

@app.route('/encounter/add', methods=['POST'])
def add_monster():
    data = request.json
    name = data['name']
    payload = {'name': str(name)}

    res = requests.get('https://api.open5e.com/monsters/', params=payload)
    json = res.json()
    monster = json['results']
    return jsonify(monster)

@app.route('/encounter/create', methods=["POST"])
def generate_encounter():
    data = request.json
    difficulty = data['difficulty']
    density = data['density']
    type = data['type']
    terrain = data['terrain']

    crs = resources.convert_xp_to_cr(difficulty, density)
    set_crs = set(crs)
    ordered = sorted(set_crs, reverse=True)
    monsters = {}

    for i, cr in enumerate(ordered):
        payload = {}
        payload['challenge_rating'] = str(cr)
        if type != 'any':
             payload['type'] = type
        res = requests.get('https://api.open5e.com/monsters/', params=payload)
        json = res.json()
        monster = random.choice(json['results'])
        monsters[f"{i}"] = monster

    return jsonify(monsters)

@app.route('/encounter/spells', methods=['POST'])
def get_spells():
    data = request.json
    spells = {}

    for i, url in data.items():
        res = requests.get(url)
        spell = res.json()
        spells[f"{i}"] = spell
    
    return jsonify(spells)