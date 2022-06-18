from flask import Flask, request, render_template, redirect, url_for
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from google.cloud import firestore
import secret
import json


class User(UserMixin):
    def __init__(self, username):
        super().__init__()
        self.id = username
        self.username = username
        self.par = {}


app = Flask(__name__)
app.config['SECRET_KEY'] = secret.secret_key

login = LoginManager(app)
login.login_view = '/static/login.html'

usersdb = {'Nonna': '12345', 'Nonno': '123'}


@login.user_loader
def load_user(username):
    if username in usersdb:
        return User(username)
    return None


@app.route('/')
def root():
    return redirect('/static/index.html')


@app.route('/main')
@login_required
def index():
    if current_user.username == 'Nonno':
        return redirect('/sensors/Nonno')
    elif current_user.username == 'Nonna':
        return redirect('/sensors/Nonna')


@app.route('/sensors/<Nonno>', methods=['GET'])
@login_required
def read_all(Nonno):
    db = firestore.Client.from_service_account_json('credentials.json')
    data = []
    for doc in db.collection(Nonno).stream():
        a = doc.to_dict()
        data.append([a['time'].split()[0], a['value']])
    return json.dumps(data)


@app.route('/sensors/Nonno', methods=['POST'])
def save_data():
    s = request.values['secret']
    if s == secret:
        time = request.values['time']
        acc = request.values['acc']
        db = firestore.Client.from_service_account_json('credentials.json')
        db.collection('Nonno').document(time).set({'time': time, 'value': acc})
        return 'ok', 200


@app.route('/sensors/Nonna', methods=['POST'])
@login_required
def save_data2():
    s = request.values['secret']
    if s == secret:
        time = request.values['time']
        acc = request.values['acc']
        db = firestore.Client.from_service_account_json('credentials.json')
        db.collection('Nonna').document(time).set({'time': time, 'value': acc})
        return 'ok', 200


@app.route('/login', methods=['POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('/main'))
    username = request.values['u']
    password = request.values['p']
    if username in usersdb and password == usersdb[username]:
        login_user(User(username))
        next_page = request.args.get('next')
        if not next_page:
            next_page = '/main'
        return redirect(next_page)
    return redirect('/static/login.html')


@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
