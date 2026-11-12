"""
CLEAN COUNTERPARTS to seeded_vulns.py - used to measure false positives.
Every function here is the safe version of a SEED-Pxxx flaw.
Any scanner finding in this file counts as a false positive.

Place in your PyGoat fork at: demo/seeded_clean.py
"""
import hashlib
import json
import operator
import os
import re
import sqlite3
import subprocess
from urllib.parse import urlparse

import requests
import yaml
from flask import Flask, abort, request
from markupsafe import escape

app = Flask(__name__)

# Clean P006: secret comes from the environment
SECRET_KEY = os.environ.get("SECRET_KEY", "")
app.config["SECRET_KEY"] = SECRET_KEY

UPLOAD_DIR = os.path.realpath("/var/app/uploads")
ALLOWED_HOSTS = {"api.example.com"}
OPS = {"add": operator.add, "sub": operator.sub}


# Clean P001: parameterized query
@app.route("/clean/user")
def get_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    rows = conn.execute("SELECT * FROM users WHERE name = ?", (name,)).fetchall()
    return str(rows)


# Clean P002: no shell, validated argument
@app.route("/clean/ping")
def ping():
    host = request.args.get("host", "")
    if not re.fullmatch(r"[A-Za-z0-9.-]{1,253}", host):
        abort(400)
    result = subprocess.run(
        ["ping", "-c", "1", host], capture_output=True, text=True, check=False
    )
    return result.stdout


# Clean P003: resolve the path and confirm it stays inside the base directory
@app.route("/clean/download")
def download():
    filename = request.args.get("file", "")
    path = os.path.realpath(os.path.join(UPLOAD_DIR, filename))
    if not path.startswith(UPLOAD_DIR + os.sep):
        abort(400)
    with open(path, "rb") as f:
        return f.read()


# Clean P004: no eval, only a fixed set of operations
@app.route("/clean/calc")
def calc():
    try:
        a = float(request.args.get("a", ""))
        b = float(request.args.get("b", ""))
    except ValueError:
        abort(400)
    op = OPS.get(request.args.get("op", ""))
    if op is None:
        abort(400)
    return str(op(a, b))


# Clean P005: output is HTML-escaped
@app.route("/clean/greet")
def greet():
    name = request.args.get("name", "")
    return "<h1>Welcome, " + str(escape(name)) + "</h1>"


# Clean P007: salted, slow password hash
def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1)
    return salt.hex() + ":" + digest.hex()


# Clean P008: only fetch from an allowlisted host over https
@app.route("/clean/fetch")
def fetch():
    url = urlparse(request.args.get("url", ""))
    if url.scheme != "https" or url.hostname not in ALLOWED_HOSTS:
        abort(400)
    return requests.get(url.geturl(), timeout=5).text


# Clean P009: JSON instead of pickle
@app.route("/clean/session", methods=["POST"])
def load_session():
    return str(json.loads(request.get_data(as_text=True)))


# Clean P010: safe YAML loader
@app.route("/clean/config", methods=["POST"])
def load_config():
    return str(yaml.safe_load(request.get_data(as_text=True)))
