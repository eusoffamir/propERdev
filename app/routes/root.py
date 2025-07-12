from flask import Blueprint, redirect, url_for

root_bp = Blueprint('root', __name__)

@root_bp.route('/')
def index():
    return redirect(url_for('auth.login')) 