
import os

from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, session)

from script import create_client, get_clients, get_config, revoke_client

app = Flask(__name__)
app.secret_key = 'mayb3_1ts_4_s3cr3t_k3y'
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
    clients_arr = get_clients()

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


@app.route("/api/clients/<name>/revoke", methods=['POST'])
def revoke(name):
    if not session.get('logged_in'):
        return redirect('/login')

    result = revoke_client(name)
    if result == None:
        return jsonify({"status": "error", "message": "Client not found"})
    if result == False:
        return jsonify({"status": "error", "message": "Client coudn't be revoked. Please try again."})
    else:
        return jsonify({"status": "success", "message": "Client revoked successfully"})


@app.route("/api/clients/<name>/create", methods=['POST'])
def create(name):
    if not session.get('logged_in'):
        return redirect('/login')

    result = create_client(name)
    if result == None:
        return jsonify({"status": "error", "message": "Client already exists"})
    elif result == False:
        return jsonify({"status": "error", "message": "Cant add client at the moment. Please try again."})
    else:
        return jsonify({"status": "success", "message": "Client created successfully"})


if __name__ == "__main__":
    if os.name == 'posix':
        if os.getuid() != 0:
            print("Please run using SUDO!")
            exit(1)
    serve(app, host="13.81.243.218", port=51821)
    from gevent.pywsgi import WSGIServer
    http_server = WSGIServer(("0.0.0.0", 51821), app)
    http_server.serve_forever()
