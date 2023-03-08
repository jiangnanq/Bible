from flask import Flask, redirect, url_for
import search

app = Flask(__name__)
app.register_blueprint(search.bp)

@app.route('/')
def root():  # put application's code here
    return redirect(url_for('search.search'))


if __name__ == '__main__':
    app.run()
