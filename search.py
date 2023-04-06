from flask import flash, Blueprint, g, redirect, render_template, request, session
from Datamanager import *

bp = Blueprint('search', __name__, url_prefix='/search')


@bp.route('/', methods=('GET', 'POST'))
def search():  # put application's code here
    if 'question' not in session.keys():
        session['question'] = ''
    if 'verses' not in session.keys():
        session['verses'] = []
    if 'gpt' not in session.keys():
        session['gpt'] = ''
    if 'sample_questions' not in session.keys() or request.method == 'GET':
        sample_questions = get_db().execute('select id, question from sample_question order by random() limit 5').fetchall()
        session['sample_questions'] = [x['id'] for x in sample_questions]

    sq = [(x, get_db().execute(f'select question from sample_question where id={x}').fetchone()['question']) for x in session['sample_questions']]
    def get_local_answer(id):
        qid = session['sample_questions'][id]
        session['question'] = get_db().execute(f'select question from sample_question where id={qid}').fetchone()['question']
        r = get_db().execute(f'select b, c from sample_answer where qid={qid}').fetchall()
        session['verses'] = [[x['b'], x['c']] for x in r]
        session['gpt'] = get_db().execute(f'select gpt from sample_gpt where qid={qid}').fetchone()['gpt']

    def get_answer():
        verses = accurateSearch(session['question']) + [getChapter(x[0], x[1]) for x in session['verses']]
        gpt = session['gpt']
        question = session['question']
        return (verses, gpt, question)

    if request.method == 'POST':
        if 'searchtext' in request.form.keys():
            if request.form['searchtext'] != '':
                question = request.form['searchtext']
                session['question'] = question
                session['verses'] = query(question)
                session['gpt'] = ask_openai(question)
        elif 'q1' in request.form.keys():
            get_local_answer(0)
        elif 'q2' in request.form.keys():
            get_local_answer(1)
        elif 'q3' in request.form.keys():
            get_local_answer(2)
        elif 'q4' in request.form.keys():
            get_local_answer(3)
        elif 'q5' in request.form.keys():
            get_local_answer(4)
    verses, gpt, question = get_answer()
    return render_template('search.html',
                           verses=verses,
                           question=question,
                           gpt=gpt,
                           sample_questions=sq)

@bp.route('/others', methods=('GET', 'POST'))
def others():
    if request.method == 'POST':
        print('submit form')
        print(session.keys())
        session.clear()
    return render_template('others.html')
