from flask import redirect, url_for, flash, g
from functools import wraps
from models import Encounter
import requests

## Decorator Functions

def already_logged_in(func):
    """Check if user is already logged in"""
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if g.user:
            flash('You are already logged in.', 'alert-danger')
            return redirect(url_for('homepage'))
        return func(*args, **kwargs)
    return decorated_func

def login_required(func):
    """Check if user is logged in and in session"""
    @wraps(func)
    def decorated_func(*args, **kwargs):
        if g.user is None:
            flash('Must be logged in to do that.', 'alert-danger')
            return redirect(url_for('handle_login'))
        return func(*args, **kwargs)
    return decorated_func

def authorized_user(func):
    """Check if the correct user is making the request"""
    @wraps(func)
    def decorated_func(*args, **kwargs):
        username = kwargs['username']
        if g.user.username != username:
            flash('Not authorized to do that.', 'alert-danger')
            return redirect('/')
        return func(*args, **kwargs)
    return decorated_func

def is_author(func):
    """Check if user is the owner of the encounter"""
    @wraps(func)
    def decorated_func(*args, **kwargs):
        encounter_id = kwargs['encounter_id']
        encounter = Encounter.query.get_or_404(encounter_id)
        if g.user.username != encounter.username:
            flash('Not authorized to do that.', 'alert-danger')
            return redirect('/')
        return func(*args, **kwargs)
    return decorated_func


def get_next(json_response, results):
    """If API response has 'next' key, add 'next' results to response"""
    if (json_response['next']):
        res = requests.get(f"{json_response['next']}")
        json = res.json()
        results += json['results']
        get_next(json, results)

