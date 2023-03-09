from flask import flash, Blueprint, g, redirect, render_template, request, session
from Datamanager import *

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/', methods=('GET', 'POST'))
def search():  # put application's code here
    answers = []
    print(session.keys())
    if request.method == 'POST':
        session['question'] = request.form['searchtext']
        print(session['question'])
        b = Bible()
        answers = b.query()
    return render_template('search.html',
                           ans=answers)

