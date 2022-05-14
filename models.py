from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.dialects.postgresql import JSON

db = SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):

    __tablename__ = 'users'

    @classmethod
    def register (cls, username, password, email):
        """hash users password"""
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode('utf8')
        return cls(username=username, password=hashed_utf8, email=email)
    
    @classmethod
    def authenticate (cls, username, password):
        """check for correct password"""
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    username = db.Column(
        db.String(20),
        primary_key=True,
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String,
        nullable=False
    )

    email = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    encounter = db.relationship('Encounter', cascade='all, delete', backref='users')

class Encounter(db.Model):

    __tablename__ = 'encounters'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )

    title = db.Column(
        db.String,
        nullable=False,
        unique=True
    )

    monsters = db.Column(
        JSON,
        nullable=False,
    )

    username = db.Column(
        db.String,
        db.ForeignKey('users.username')
    )