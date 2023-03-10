from flask import Flask, redirect, url_for, session
import search
import os
from datetime import timedelta

app = Flask(__name__)

app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'bible_chn.db'),
    )

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=1)

app.register_blueprint(search.bp)

@app.route('/')
def root():  # put application's code here
    return redirect(url_for('search.search'))


if __name__ == '__main__':
    app.run()
