from flask import flash, Blueprint, g, redirect, render_template

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/')
def search():  # put application's code here
    if
    return render_template('search.html')

