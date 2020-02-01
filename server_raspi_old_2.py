from flask import Flask, render_template, request, redirect, url_for, escape, session, abort, flash
from flask_bootstrap import Bootstrap
import flask_login
import json
import sqlite3
import datetime
import os

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
             builder text,
             type text,
             time datetime
             )""")

c.execute("""CREATE TABLE stations(
             id text PRIMARY KEY,
             type text
             )""")

c.close()


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


@app.route('/setnewspeed/<builder>', methods=['GET', 'POST'])
def set_new_speed(builder):
    speed = request.form['speed']
    now = datetime.datetime.now()
    time = now.isoformat()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM events WHERE type = "SLOW"''')
    count = c.fetchall()
    count = count[0][0]
    builder_id = builder[0] + builder[len(builder) - 1]
    event_id = 'SPE' + str(count) + builder_id
    with conn:
        c.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
                  (event_id, builder, 'CHANGED SPEED', time))
    print(builder + ' changed speed to ' + speed)
    return render_template('mainview.html')


@app.route('/slowbuilder/<builder>', methods=['GET', 'POST'])
def slow_builder(builder):
    now = datetime.datetime.now()
    time = now.isoformat()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM events WHERE type = "SLOW"''')
    count = c.fetchall()
    count = count[0][0]
    builder_id = builder[0] + builder[len(builder) - 1]
    event_id = 'SLO' + str(count) + builder_id
    with conn:
        c.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
                  (event_id, builder, 'SLOW', time))
    print(builder + ' is running at half speed')
    return render_template('mainview.html')


@app.route('/startbuilder/<builder>', methods=['GET', 'POST'])
def start_builder(builder):
    now = datetime.datetime.now()
    time = now.isoformat()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM events''')
    count = c.fetchall()
    count = count[0][0]
    builder_id = builder[0] + builder[len(builder) - 1]
    event_id = 'STA' + str(count) + builder_id
    with conn:
        c.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
                  (event_id, builder, 'START', time))
    print(builder + ' started')
    return render_template('mainview.html')


@app.route('/stopbuilder/<builder>', methods=['GET', 'POST'])
def stop_builder(builder):
    now = datetime.datetime.now()
    time = now.isoformat()
    c = conn.cursor()
    c.execute('''SELECT COUNT(*) FROM events WHERE type = "STOP"''')
    count = c.fetchall()
    count = count[0][0]
    builder_id = builder[0] + builder[len(builder) - 1]
    event_id = 'STO' + str(count) + builder_id
    with conn:
        c.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
                  (event_id, builder, 'STOP', time))
    print(builder + ' stopped')
    return render_template('mainview.html')


#*@app.route('/disableuilder/<builder>', methods=['GET', 'POST'])
#def disable_builder(builder):
#    now = datetime.datetime.now()
#    time = now.isoformat()
#    c = conn.cursor()
#    c.execute('''SELECT COUNT(*) FROM events WHERE type = "DISABLED"''')
#    count = c.fetchall()
#    count = count[0][0]
#    builder_id = builder[0] + builder[len(builder) - 1]
#    event_id = 'STO' + str(count) + builder_id
#    with conn:
#        c.execute('INSERT INTO events VALUES (?, ?, ?, ?)',
#                  (event_id, builder, 'STOP', time))
#    print(builder + ' stopped')


@app.route('/build/', methods=['POST'])
def build():
    insert_robot(request.get_json())
    return render_template('built.html')


@app.route('/oee/<builder>/', methods=['GET'])
def OEE_builder(builder):
    c = conn.cursor()
    builder_s = "'" + builder + "'"
    c.execute('''SELECT COUNT(*) FROM robots WHERE builder = ''' + builder_s + ''' AND quality = "PERFECT"''')
    perfect = c.fetchall()
    perfect = int(perfect[0][0])
    print(perfect)
    c.execute('''SELECT COUNT(*) FROM robots WHERE builder = ''' + builder_s + ''' AND quality = "GOOD"''')
    good = c.fetchall()
    good = int(good[0][0])
    c.execute('''SELECT COUNT(*) FROM robots WHERE builder = ''' + builder_s + ''' AND quality = "UNUSABLE"''')
    unusable = c.fetchall()
    unusable = int(unusable[0][0])
    c.close()
    return render_template('chartview.html', builder=builder, perfect=perfect, good=good, unusable=unusable)


@app.route('/robotsbybuilder/<builder>/', methods=['GET'])
def robots_by_builder(builder):
    c = conn.cursor()
    builder_s = "'" + builder + "'"
    c.execute('''SELECT * FROM robots WHERE builder = ''' + builder_s)
    rows = c.fetchall()
    c.close()
    return render_template('databaseview-robots.html', builder=builder, rows=rows)


@app.route('/allrobots/', methods=['GET'])
def all_robots():
    c = conn.cursor()
    c.execute('''SELECT * FROM robots''')
    rows = c.fetchall()
    c.close()
    return render_template('databaseview-robots.html', rows=rows)


@app.route('/eventsbybuilder/<builder>/', methods=['GET'])
def events_by_builder(builder):
    c = conn.cursor()
    builder_s = "'" + builder + "'"
    c.execute('''SELECT * FROM events WHERE builder = ''' + builder_s)
    rows = c.fetchall()
    c.close()
    return render_template('databaseview-events.html', builder=builder, rows=rows)


@app.route('/allevents/', methods=['GET'])
def all_events():
    c = conn.cursor()
    c.execute('''SELECT * FROM events''')
    rows = c.fetchall()
    c.close()
    return render_template('databaseview-events.html', rows=rows)


def insert_robot(robot):
    c = conn.cursor()
    now = datetime.datetime.now()
    time = now.isoformat()
    robot_dict = json.loads(robot)
    print(robot_dict)
    with conn:
        c.execute('INSERT INTO robots VALUES (?, ?, ?, ?, ?)',
                  (robot_dict['id'], robot_dict['color'], robot_dict['quality'], robot_dict['builder'], time))
    c.close()


if __name__ == '__main__':  # always use to run server by python directly
    app.secret_key = os.urandom(12)
    app.run(host='0.0.0.0', debug=True)
