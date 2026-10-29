import re
import sqlite3
import subprocess
import ast
import operator
from flask import Flask, request

app = Flask(__name__)

_ALLOWED_BIN_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_ALLOWED_UNARY_OPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

def _safe_eval_expr(expr):
    node = ast.parse(expr, mode="eval")

    def _eval(n):
        if isinstance(n, ast.Expression):
            return _eval(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in _ALLOWED_BIN_OPS:
            return _ALLOWED_BIN_OPS[type(n.op)](_eval(n.left), _eval(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in _ALLOWED_UNARY_OPS:
            return _ALLOWED_UNARY_OPS[type(n.op)](_eval(n.operand))
        raise ValueError("Invalid expression")

    return _eval(node)

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
    expr = request.args.get("expr", "")
    try:
        return str(_safe_eval_expr(expr))
    except Exception:
        return "Invalid expression", 400
