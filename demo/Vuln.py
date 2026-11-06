import hashlib
import logging
import os
import pickle
import random
import sqlite3
import subprocess
import xml.etree.ElementTree as ET
from xml.sax import make_parser, handler  

import requests
import yaml
from flask import Flask, request, redirect, render_template_string, make_response, session, send_file

app = Flask(__name__)
app.secret_key = "supersecret123"  
app.config["DEBUG"] = True  

DB_PASSWORD = "admin:Passw0rd!"  
AWS_SECRET_KEY = "AKIAIOSFODNN7EXAMPLE/wJalrXUtnFEMI/K7MDENG" 

logging.basicConfig(filename="app.log", level=logging.DEBUG)


def db():
    return sqlite3.connect("app.db")


@app.route("/user")
def get_user():
    name = request.args.get("name", "")
    cur = db().cursor()
    cur.execute("SELECT * FROM users WHERE name = '%s'" % name)
    return str(cur.fetchall())


@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    return subprocess.check_output("ping -c 1 " + host, shell=True)  


@app.route("/calc")
def calc():
    expr = request.args.get("expr", "1+1")
    return str(eval(expr)) 


@app.route("/greet")
def greet():
    name = request.args.get("name", "")
    return render_template_string("<h1>Hello " + name + "</h1>")  


@app.route("/search")
def search():
    q = request.args.get("q", "")
    return "<p>Results for: %s</p>" % q 


@app.route("/ldap")
def ldap_lookup():
    uid = request.args.get("uid", "")
    flt = "(&(objectClass=person)(uid=" + uid + "))"  
    return flt


@app.route("/download")
def download():
    fname = request.args.get("file", "")
    return send_file(os.path.join("/var/app/files", fname))  


@app.route("/upload", methods=["POST"])
def upload():
    f = request.files["file"]
    f.save(os.path.join("uploads", f.filename))
    return "ok"


@app.route("/load", methods=["POST"])
def load_obj():
    return str(pickle.loads(request.data))  

@app.route("/yaml", methods=["POST"])
def load_yaml():
    return str(yaml.load(request.data, Loader=yaml.Loader))  


@app.route("/xml", methods=["POST"])
def parse_xml():
    root = ET.fromstring(request.data)  
    return root.tag


@app.route("/fetch")
def fetch():
    url = request.args.get("url", "")
    return requests.get(url, verify=False).text


@app.route("/go")
def go():
    return redirect(request.args.get("next", "/"))


@app.route("/transfer", methods=["POST"]) 
def transfer():
    amount = request.form["amount"]
    to = request.form["to"]
    return "Transferred %s to %s" % (amount, to)


def hash_pw(pw):
    return hashlib.md5(pw.encode()).hexdigest() 


@app.route("/login", methods=["POST"])
def login():
    u, p = request.form["user"], request.form["pass"]
    cur = db().cursor()
    cur.execute("SELECT id FROM users WHERE name=? AND pw=?", (u, hash_pw(p)))
    row = cur.fetchone()
    if row:
        session["uid"] = row[0]
        resp = make_response("welcome")
        resp.set_cookie("auth", str(row[0]))
        return resp
    logging.info("Failed login for %s with password %s", u, p)
    return "Invalid username", 401 

@app.route("/reset_token")
def reset_token():
    return str(random.randint(100000, 999999)) 


@app.route("/profile/<int:user_id>")
def profile(user_id):
    cur = db().cursor()
    cur.execute("SELECT * FROM users WHERE id=?", (user_id,))  
    return str(cur.fetchall())


@app.route("/admin/delete_all")
def admin_delete_all():
    db().execute("DELETE FROM users")
    return "deleted"


@app.route("/is_admin")
def is_admin():
    if request.cookies.get("role") == "admin": 
        return "admin panel"
    return "denied"


def encrypt(data: bytes) -> bytes:
    from Crypto.Cipher import DES  
    key = b"8bytekey" 
    return DES.new(key, DES.MODE_ECB).encrypt(data.ljust(16))


@app.route("/update_user", methods=["POST"])
def update_user():
    fields = request.form.to_dict() 
    sets = ", ".join("%s='%s'" % kv for kv in fields.items()) 
    db().execute("UPDATE users SET " + sets + " WHERE id=%d" % session["uid"])
    return "updated"


@app.route("/debug")
def debug_info():
    return str(dict(os.environ))


@app.errorhandler(Exception)
def handle(e):
    import traceback
    return traceback.format_exc(), 500


@app.route("/tmpfile")
def tmpfile():
    path = "/tmp/report.txt" 
    with open(path, "w") as f:
        f.write(request.args.get("data", ""))
    os.chmod(path, 0o777)  
    return path


@app.route("/withdraw", methods=["POST"])
def withdraw():
    balance = int(request.form["balance"])
    amount = int(request.form["amount"])
    return str(balance - amount)


@app.route("/regex")
def regex():
    import re
    return str(bool(re.match(r"^(a+)+$", request.args.get("s", ""))))  


@app.route("/headers")
def headers():
    resp = make_response("ok")
    resp.headers["X-Custom"] = request.args.get("v", "") 
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


@app.route("/assert")
def assert_check():
    assert session.get("uid"), "must be logged in"
    return "ok"


def read_config(path):
    try:
        return open(path).read() 
    except:  
        pass


@app.route("/xml_bomb", methods=["POST"])
def xml_bomb():
    import xml.dom.minidom
    doc = xml.dom.minidom.parseString(request.data)  
    return doc.documentElement.tagName


@app.route("/register", methods=["POST"])
def register():
    user = request.form["user"]
    pw = request.form["pass"]
    with open("users.txt", "a") as f:
        f.write("%s:%s\n" % (user, pw)) 
    logging.info("Registered %s with password %s", user, pw)  
    print("new user password:", pw) 
    resp = make_response("registered")
    resp.set_cookie("pw", pw) 
    return resp


@app.route("/cookie_pref")
def cookie_pref():
    resp = make_response("saved")
    resp.set_cookie("theme", request.args.get("theme", "")) 
    resp.headers["Set-Cookie"] = "lang=" + request.args.get("lang", "en") 
    return resp


DOM_PAGE = """<!doctype html>
<html><head>
<script src="https://cdn.jsdelivr.net/npm/jquery/dist/jquery.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap/dist/css/bootstrap.min.css">
</head><body>
<!-- VULN: CWE-830 script/stylesheet from third-party CDN without integrity (SRI) or crossorigin -->
<input id="in" value="">
<div id="out"></div>
<script>
  // VULN: CWE-79/CWE-116 DOM text reinterpreted as HTML
  document.getElementById("out").innerHTML = document.getElementById("in").value;
  var h = decodeURIComponent(location.hash.substring(1));
  document.write(h);  // VULN: CWE-79 DOM XSS via location.hash
</script>
</body></html>"""


@app.route("/dom")
def dom():
    return DOM_PAGE


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True) 
