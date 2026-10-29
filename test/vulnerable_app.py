import ast
import re
import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)

def _safe_eval_arithmetic(expr: str):
    tree = ast.parse(expr, mode="eval")

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Constant,
        ast.Num,  # compatibility with older Python versions
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.FloorDiv,
        ast.Mod,
        ast.Pow,
        ast.UAdd,
        ast.USub,
    )

    for node in ast.walk(tree):
        if not isinstance(node, allowed_nodes):
            raise ValueError("Disallowed expression")

    return eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, {})

@app.route("/user")
def get_user():
    name = request.args.get("name")
    conn = sqlite3.connect("app.db")
    # Use a parameterized query to prevent SQL injection
    query = "SELECT * FROM users WHERE name = ?"
    return str(conn.execute(query, (name,)).fetchall())

@app.route("/ping")
def ping():
    host = request.args.get("host", "")
    # Validate host input and avoid shell invocation to prevent command injection
    if not host or not re.fullmatch(r"[A-Za-z0-9.-]+", host):
        return "Invalid host", 400
    return subprocess.check_output(["ping", "-c", "1", host], shell=False, text=True)

@app.route("/calc")
def calc():
    expr = request.args.get("expr", "")
    if not expr:
        return "Invalid expression", 400
    try:
        return str(_safe_eval_arithmetic(expr))
    except Exception:
        return "Invalid expression", 400
