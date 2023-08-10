
from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, session)

from script import get_clients, get_config, revoke_client

# For UNIX systems only
# if os.getuid() != 0:
#     print("Please run using SUDO!")
#     exit(1)

app = Flask(__name__)
# change this to an environment variable
app.secret_key = 'mayb3_1ts_4_s3cr3t_k3y'

# change this to an environment variable
PASSWORD = 'eef2decbc5d8f20aaeaf63e2ac8371aee5d0b4733770aef60cfa116a88b5f28c'


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


@app.route("/api/clients", methods=['GET'])
def clients():
    if not session.get('logged_in'):
        return redirect('/login')
    # clients_arr = get_clients()
    clients_arr = [
        {"bytes_recv": 0, "bytes_sent": 0, "connected": False, "connected_since": None,
            "last_ref": None, "name": "ubu", "real_ip": None, "virtual_ip": None},
        {"bytes_recv": "154143", "bytes_sent": "152792", "connected": True, "connected_since": "2023-08-09 04:33:54", "last_ref": "2023-08-09 10:26:03",
         "name": "lubuntu", "real_ip": "192.168.1.6:59567", "virtual_ip": "10.8.0.2"},
        {"bytes_recv": "77863", "bytes_sent": "75930", "connected": True, "connected_since": "2023-08-09 08:14:51",
            "last_ref": "2023-08-09 10:29:33", "name": "lubuntu2", "real_ip": "192.168.1.4:58613", "virtual_ip": "10.8.0.3"},
        {"bytes_recv": 0, "bytes_sent": 0, "connected": False, "connected_since": None,
            "last_ref": None, "name": "test", "real_ip": None, "virtual_ip": None}
    ]
    # clients_arr = []

    return jsonify(clients_arr)


@app.route("/api/clients/<name>/config", methods=['GET'])
def config(name):
    if not session.get('logged_in'):
        return redirect('/login')

    result = get_config(name)
    if result == None:
        return jsonify({"status": "error", "message": "Client not found"})
    else:
        return send_file(result, as_attachment=True)


@app.route("/api/clients/<name>/revoke", methods=['GET'])
def revoke(name):
    if not session.get('logged_in'):
        return redirect('/login')

    result = revoke_client(name)
    if result == None:
        return jsonify({"status": "error", "message": "Client not found"})
    else:
        return jsonify({"status": "success", "message": "Client revoked successfully"})


@app.route("/api/clients/<name>/create", methods=['GET'])
def create(name):
    if not session.get('logged_in'):
        return redirect('/login')

    result = create_client(name)
    if result == None:
        return jsonify({"status": "error", "message": "Client already exists"})
    else:
        # dont forget to refresh the page on frontend when this is called
        return jsonify({"status": "success", "message": "Client created successfully"})
