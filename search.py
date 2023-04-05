from flask import flash, Blueprint, g, redirect, render_template, request, session
from Datamanager import *
import random

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/', methods=('GET', 'POST'))
def search():  # put application's code here
    with open('questions.txt', 'r') as f:
        questions = f.read()
    questions = questions.split('\n')
    sample_questions = random.sample(questions, 5)
    verses = []
    question = ''
    gpt = ''
    if request.method == 'POST':
        if request.form['searchtext'] != '':
            question = request.form['searchtext']
            b = Bible()
            verses = b.query(question)
            gpt = ask_openai(question)
    return render_template('search.html',
                           verses=verses,
                           question=question,
                           gpt=gpt,
                           sample_questions=sample_questions)

@bp.route('/others', methods=('GET', 'POST'))
def others():
    if request.method == 'POST':
        print('submit form')
        print(session.keys())
        session.clear()
    return render_template('others.html')
