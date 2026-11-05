"""
SEEDED VULNERABLE CODE - FOR SCANNER EVALUATION ONLY
Intentionally insecure. Do not run, deploy, or expose this file.
Each flaw is tagged SEED-Pxxx so results can be matched to manifest_pygoat.csv.

Place in your PyGoat fork at: demo/seeded_vulns.py
(do NOT put it under a "test" folder; CodeQL hides alerts in test code).
Standalone Flask app: PyGoat is Django and never imports this file.
"""
import hashlib
import os
import pickle
import sqlite3
import subprocess

import requests
import yaml
from flask import Flask, request

app = Flask(__name__)

# SEED-P006: hard-coded secret (CWE-798)
SECRET_KEY = "pygoat-secret-key-123"
app.config["SECRET_KEY"] = SECRET_KEY


# SEED-P001: SQL injection (CWE-89)
@app.route("/seed/user")
def get_user():
    name = request.args.get("name", "")
    conn = sqlite3.connect("app.db")
    query = "SELECT * FROM users WHERE name = '" + name + "'"
    return str(conn.execute(query).fetchall())


# SEED-P002: OS command injection (CWE-78)
@app.route("/seed/ping")
def ping():
    host = request.args.get("host", "")
    return subprocess.check_output("ping -c 1 " + host, shell=True)


# SEED-P003: path traversal (CWE-22)
@app.route("/seed/download")
def download():
    filename = request.args.get("file", "")
    path = os.path.join("/var/app/uploads", filename)
    with open(path, "rb") as f:
        return f.read()


# SEED-P004: code injection via eval (CWE-94)
@app.route("/seed/calc")
def calc():
    expr = request.args.get("expr", "")
    return str(eval(expr))


# SEED-P005: reflected cross-site scripting (CWE-79)
@app.route("/seed/greet")
def greet():
    name = request.args.get("name", "")
    return "<h1>Welcome, " + name + "</h1>"


# SEED-P007: weak password hashing (CWE-327 / CWE-328)
def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()


# SEED-P008: server-side request forgery (CWE-918)
@app.route("/seed/fetch")
def fetch():
    url = request.args.get("url", "")
    return requests.get(url, timeout=5).text


# SEED-P009: insecure deserialization with pickle (CWE-502)
@app.route("/seed/session", methods=["POST"])
def load_session():
    blob = request.get_data()
    return str(pickle.loads(blob))


# SEED-P010: unsafe YAML loading (CWE-502)
@app.route("/seed/config", methods=["POST"])
def load_config():
    text = request.get_data(as_text=True)
    return str(yaml.load(text, Loader=yaml.Loader))
