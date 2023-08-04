from flask import Flask, jsonify, redirect, render_template, request, session

app = Flask(__name__)
app.secret_key = 'mayb3_1ts_4_s3cr3t_k3y'

PASSWORD = 'eef2decbc5d8f20aaeaf63e2ac8371aee5d0b4733770aef60cfa116a88b5f28c'
clients_arr = []
ident: int = 0


def hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


@app.route("/")
def default():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if hash(request.form['password']) == PASSWORD:
            session['logged_in'] = True
            return redirect('/')
        return render_template('login.html', error='Wrong password')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect('/login')

# this will get all the clients


@app.route("/api/clients", methods=['GET'])
def clients():
    if not session.get('logged_in'):
        return redirect('/login')
    import random

    return jsonify([
        {
            'id': random.randint(0, 100),
            'name': 'Client ' + str(random.randint(0, 100)),
            'status': random.choice(['online', 'offline'])
        }
        for _ in range(10)

    ])

# this will refetch the connected clients


@app.route("/api/clients/status", methods=['GET'])
def clients_status():
    if not session.get('logged_in'):
        return redirect('/login')
    return jsonify(clients_arr)
