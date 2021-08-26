from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pineapple import Pineapple
import logging
import serial

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True

socketio = SocketIO(app=app, async_mode=None)

pineapple_thread = Pineapple(socketio=socketio)


@app.after_request
def add_header(r):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/debugger")
def debugger():
    return render_template("debugger.html")


@socketio.on("ports", namespace="/pineapple")
def ports():
    names = []
    descriptions = []

    for i in pineapple_thread.arduino.scan_ports():
        names.append(i.device)
        descriptions.append(i.description)

    emit("ports_result", {
        "ports": names,
        "descriptions": descriptions
    }, broadcast=True)


@socketio.on("connect_port", namespace="/pineapple")
def connect_port(data):
    pineapple_thread.arduino.start(data["port"])


@socketio.on("plus_count", namespace="/pineapple")
def connect_port(data):
    pineapple_thread.target_count = pineapple_thread.data.pulse_count + data["plus"]


@socketio.on("connect", namespace="/pineapple")
def connect():
    pineapple_thread.send_code()
    emit("cpu_busy", pineapple_thread.data.CPU_BUSY)
    emit("pulse_counter", pineapple_thread.data.pulse_count)
    emit("u_counter", pineapple_thread.data.uCounter)
    # emit("running", pineapple_thread.data.pulse_count)


@socketio.on("start", namespace="/pineapple")
def start(data):
    global pineapple_thread

    pineapple_thread.debug = data["debug"]

    if not pineapple_thread.is_alive():
        pineapple_thread.start()


@socketio.on("stop", namespace="/pineapple")
def stop():
    global pineapple_thread

    if pineapple_thread.is_alive():
        pineapple_thread.stop()
        pineapple_thread = Pineapple(socketio=socketio)


@socketio.on("restart", namespace="/pineapple")
def restart():
    global pineapple_thread

    if pineapple_thread.is_alive():
        pineapple_thread.stop()
        pineapple_thread = Pineapple(socketio=socketio)

    if not pineapple_thread.is_alive():
        pineapple_thread.start()


if __name__ == "__main__":
        
    socketio.run(host="0.0.0.0", app=app, log_output=1)
