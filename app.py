
import os

from flask import (Flask, jsonify, redirect, render_template, request,
                   send_file, session)
from flask_socketio import SocketIO
import pty
import subprocess
import select
import termios
import struct
import fcntl
import shlex
import logging
import sys

from script import create_client, get_clients, get_config, revoke_client

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = 'mayb3_1ts_4_s3cr3t_k3y'
PASSWORD = 'eef2decbc5d8f20aaeaf63e2ac8371aee5d0b4733770aef60cfa116a88b5f28c'
app.config["fd"] = None
app.config["child_pid"] = None
socketio = SocketIO(app)

def hash(password):
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def set_winsize(fd, row, col, xpix=0, ypix=0):
    logging.debug("setting window size with termios")
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)


def read_and_forward_pty_output():
    max_read_bytes = 1024 * 20
    while True:
        socketio.sleep(0.01)
        if app.config["fd"]:
            timeout_sec = 0
            (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
            if data_ready:
                output = os.read(app.config["fd"], max_read_bytes).decode(
                    errors="ignore"
                )
                socketio.emit("pty-output", {"output": output}, namespace="/pty")


@app.route("/terminal")
def terminal():
    if not session.get('logged_in'):
        return redirect('/login')
    return render_template("terminal.html")

@socketio.on("pty-input", namespace="/pty")
def pty_input(data):
    """write to the child pty. The pty sees this as if you are typing in a real
    terminal.
    """
    if not session.get('logged_in'):
        return redirect('/login')
    if app.config["fd"]:
        logging.debug("received input from browser: %s" % data["input"])
        os.write(app.config["fd"], data["input"].encode())


@socketio.on("resize", namespace="/pty")
def resize(data):
    if not session.get('logged_in'):
        return redirect('/login')
    if app.config["fd"]:
        logging.debug(f"Resizing window to {data['rows']}x{data['cols']}")
        set_winsize(app.config["fd"], data["rows"], data["cols"])


@socketio.on("connect", namespace="/pty")
def connect():
    """new client connected"""
    if not session.get('logged_in'):
        return redirect('/login')
    logging.info("new client connected")
    if app.config["child_pid"]:
        # already started child process, don't start another
        return

    # create child process attached to a pty we can read from and write to
    (child_pid, fd) = pty.fork()
    if child_pid == 0:
        # this is the child process fork.
        # anything printed here will show up in the pty, including the output
        # of this subprocess
        subprocess.run(app.config["cmd"])
    else:
        # this is the parent process fork.
        # store child fd and pid
        app.config["fd"] = fd
        app.config["child_pid"] = child_pid
        set_winsize(fd, 50, 50)
        cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
        # logging/print statements must go after this because... I have no idea why
        # but if they come before the background task never starts
        socketio.start_background_task(target=read_and_forward_pty_output)

        logging.info("child pid is " + child_pid)
        logging.info(
            f"starting background task with command `{cmd}` to continously read "
            "and forward pty output to client"
        )
        logging.info("task started")


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

    app.config["cmd"] = "bash"
    green = "\033[92m"
    end = "\033[0m"
    log_format = (
        green
        + "pyxtermjs > "
        + end
        + "%(levelname)s (%(funcName)s:%(lineno)s) %(message)s"
    )
    logging.basicConfig(
        format=log_format,
        stream=sys.stdout,
        level=logging.INFO,
    )
    socketio.run(app, port=51821, host="0.0.0.0")

    # from gevent.pywsgi import WSGIServer
    # http_server = WSGIServer(("0.0.0.0", 51821), app)
    # http_server.serve_forever()
