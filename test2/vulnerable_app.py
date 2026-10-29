import re
import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)

@app.route("/user")
def get_user():
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    # Safe parameterized query
    query = "SELECT * FROM users WHERE name = ?"
    return str(conn.execute(query, (name,)).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    if not re.fullmatch(r"[A-Za-z0-9.\-:]+", host):
        return "Invalid host", 400
    return subprocess.check_output(["ping", "-c", "1", host])

@app.route("/calc")
def calc():
    expr = request.args.get("expr")
    # Code injection: user input passed to eval
    return str(eval(expr))
