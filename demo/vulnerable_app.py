import sqlite3
import subprocess

from flask import Flask, request

app = Flask(__name__)

SECRET_KEY = "pygoat-secret-key-123"
app.config["SECRET_KEY"] = SECRET_KEY


@app.route("/seed/user")
def get_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    return str(conn.execute(query).fetchall())


@app.route("/seed/ping")
def ping():
    host = request.args.get("host", "")
    return subprocess.check_output("ping -c 1 " + host, shell=True)
