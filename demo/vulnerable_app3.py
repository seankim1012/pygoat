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
