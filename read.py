from flask import flash, Blueprint, g, redirect, render_template, request, session
from Datamanager import *

bp = Blueprint('read', __name__, url_prefix='/read')


@bp.route('/<book>/<chapter>', methods=('GET', 'POST'))
def read(book=0, chapter=0):  # put application's code here
    if 'select_book' not in session.keys():
        session['select_book'] = 1
    if 'select_chapter' not in session.keys():
        session['select_chapter'] = 1
    if 'select_verses' not in session.keys():
        session['select_verses'] = ''
    if 'show_quote' not in session.keys():
        session['show_quote'] = False
    if 'chapters' not in session.keys():
        session['chapters'] = [x['c'] for x in get_db().execute(
            f'select distinct c from t_chn where b={session["select_book"]}').fetchall()]
    if 'selectall' not in request.form.keys():
        session['selectall'] = False

    if int(book) > 0:
        session['select_book'] = int(book)
        session['chapters'] = [x['c'] for x in get_db().execute(
            f'select distinct c from t_chn where b={session["select_book"]}').fetchall()]
        if int(chapter) > 0:
            session['select_chapter'] = int(chapter)
        else:
            session['select_chapter'] = 1

    if request.method == 'POST':
        if 'verse' in request.form.keys():
            verses_id = sorted(request.form.getlist('verse'), key=lambda x: int(x))
            print(verses_id)
            def getverse(v):
                return get_db().execute(f'select t from t_chn where b={session["select_book"]} and c={session["select_chapter"]} and v={v}').fetchone()['t']
            if verses_id:
                session['select_verses'] = ' '.join([getverse(x) for x in verses_id])
                bookname = get_db().execute(f'select FullName from BibleID where SN={session["select_book"]}').fetchone()['FullName']
                if len(verses_id) == 1:
                    session['select_verses'] = f'{bookname} {session["select_chapter"]}:{verses_id[0]} ' + session['select_verses']
                else:
                    session['select_verses'] = f'{bookname} {session["select_chapter"]}:{verses_id[0]}-{verses_id[-1]} ' + session['select_verses']
                print(session['select_verses'])
        else:
            session['select_verses'] = ''
        if 'show_quote' in request.form.keys() and request.form['show_quote']:
            session['show_quote'] = True
        else:
            session['show_quote'] = False
        session['select_book'] = int(request.form['book'])
        session['chapters'] = [x['c'] for x in get_db().execute(
            f'select distinct c from t_chn where b={session["select_book"]}').fetchall()]
        if 'chapter' in request.form.keys():
            if int(request.form['chapter']) in session['chapters']:
                session['select_chapter'] = int(request.form['chapter'])
        else:
            session['select_chapter'] = 1
    v = get_db().execute(f'select tc.id, tc.v, tc.t, count() from t_chn tc left join cross_reference r on tc.id=r.vid '
                         f'where tc.b={session["select_book"]} and tc.c={session["select_chapter"]} '
                         f'group by tc.id').fetchall()
    verses = [(x['v'], x['t'], x['id'], x[3]) for x in v]
    books = [(x['SN'], x['FullName']) for x in
             get_db().execute('select SN, FullName from BibleID').fetchall()]
    return render_template('read.html',
                           books=books,
                           verses=verses)


@bp.route('/verse/<id>', methods=('GET', 'POST'))
def verse(id):
    r = get_db().execute(f'select b, c, v, t from t_chn where id={id}').fetchone()
    bookname = get_db().execute(f'select FullName from BibleID where SN={r["b"]}').fetchone()['FullName']
    title = f'{bookname} {r["c"]}:{r["v"]}    {r["t"]}'
    ref = get_db().execute(
        f'select c.sv, c.ev from cross_reference c left join t_chn r on c.vid=r.id where c.vid={id}').fetchall()

    def get_verse(sv, ev):
        if ev != 0:
            t = get_db().execute(f'select t from t_chn where id between {sv} and {ev}').fetchall()
        else:
            t = get_db().execute(f'select t from t_chn where id={sv}').fetchall()
        t = ' '.join([x['t'] for x in t])
        r = get_db().execute(f'select b, c, v from t_chn where id={sv}').fetchone()
        bookname = get_db().execute(f'select FullName from BibleID where SN={r["b"]}').fetchone()['FullName']
        return (f'{bookname} {r["c"]}:{r["v"]}', f'{t}', r['b'], r['c'])
    ref = [get_verse(x['sv'], x['ev']) for x in ref]
    return render_template('verse.html',
                           title=title,
                           ref=ref)
