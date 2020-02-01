from flask import Flask, render_template, request, redirect, url_for, escape, session, abort, flash
from flask_bootstrap import Bootstrap
import flask_login
import json
import sqlite3
import datetime
import os

# TODO
# Amount of products, stations ect as int vs counted from db???

app = Flask(__name__)
login_manager = flask_login.LoginManager()
Bootstrap(app)
conn = sqlite3.connect(':memory:', check_same_thread=False)
c = conn.cursor()

logged_in_name = ""

c.execute("""CREATE TABLE robots (
             id text PRIMARY KEY,
             color text,
             quality text,
             builder text,
             time datetime
             )""")

c.execute("""CREATE TABLE events (
             id text PRIMARY KEY,
             type text,
             time datetime
             )""")

c.execute("""CREATE TABLE stations(
             id text PRIMARY KEY,
             type text
             )""")


@app.route('/')
def home():
    return render_template('home.html', loginstatus=session.get('logged_in'))


@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == 'admin':
        session['logged_in'] = True
        return redirect('/mainview')
    else:
        flash('Invalid login creditentials!')
        return render_template('login.html', message='Invalid login creditentials!')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()


@app.route('/loginpage',  methods=['GET'])
def display_login_page():
    return render_template('login.html')


@app.route('/mainview', methods=['GET', 'POST'])
def main_view():
    return render_template('mainview.html')


@app.route('/stopmachine/', methods=['POST'])
def feed():
    return 1


@app.route('/build/', methods=['POST'])
def build():
    insert_robot(request.get_json())
    return render_template('built.html')


@app.route('/allrobots/', methods=['GET'])
def all_robots():
    c.execute('''SELECT * FROM robots''')
    rows = c.fetchall()
    return render_template('databaseview.html', rows=rows)


def insert_robot(robot):
    now = datetime.datetime.now()
    time = now.isoformat()
    robot_dict = json.loads(robot)
    print(robot_dict)
    with conn:
        c.execute('INSERT INTO robots VALUES (?, ?, ?, ?, ?)',
                  (robot_dict['id'], robot_dict['color'], robot_dict['quality'], robot_dict['builder'], time))


if __name__ == '__main__':  # always use to run server by python directly
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', debug=True)
