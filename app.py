import os, sqlite3, hashlib
from flask import Flask, render_template, request, redirect, jsonify, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecret"

# Use absolute paths so file operations work regardless of CWD
DB = os.path.join(app.root_path, "database.db")
UPLOAD = os.path.join(app.root_path, "static", "photos")
# Ensure upload directory exists
os.makedirs(UPLOAD, exist_ok=True)

def db():
    return sqlite3.connect(DB, check_same_thread=False)

def init_db():
    with db() as con:
        con.executescript(open("schema.sql").read())

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u = request.form.get("username")
        p = hashlib.sha256(request.form.get("password", "").encode()).hexdigest()
        with db() as con:
            cur = con.execute("SELECT id FROM users WHERE username=? AND password=?", (u, p))
            if cur.fetchone():
                session["user"] = u
                return redirect("/admin")
            else:
                error = "Invalid username or password"
                return render_template("login.html", error=error)
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def auth():
    return "user" in session

@app.route("/")
def map_page():
    # Pass auth flag so the map page can enable add-pin UI for signed-in users
    return render_template("map.html", auth=auth())

@app.route("/api/pins")
def pins():
    with db() as con:
        rows = con.execute("SELECT * FROM pins").fetchall()
    keys = ["id", "name", "lat", "lng", "description", "photo_filename", "date"]
    return jsonify([dict(zip(keys, r)) for r in rows])

@app.route("/admin")
def admin():
    if not auth(): return redirect("/login")
    with db() as con:
        pins = con.execute("SELECT * FROM pins").fetchall()
    return render_template("admin.html", pins=pins)

@app.route("/api/pins/add", methods=["POST"])
def add_pin():
    if not auth(): return "unauth",403
    f=request.files.get("photo")
    filename=None
    if f:
        if f.filename:
            filename = secure_filename(f.filename)
            f.save(os.path.join(UPLOAD, filename))
    con = db()
    try:
        con.execute(
            "INSERT INTO pins (name,lat,lng,description,photo_filename,date) VALUES (?,?,?,?,?,?)",
            (
                request.form.get("name"),
                request.form.get("lat"),
                request.form.get("lng"),
                request.form.get("description"),
                filename,
                request.form.get("date"),
            ),
        )
        con.commit()
    finally:
        con.close()
    return redirect("/admin")

@app.route("/api/pins/delete/<int:id>", methods=["POST"])
def delete(id):
    if not auth(): return "unauth",403
    con = db()
    try:
        con.execute("DELETE FROM pins WHERE id=?", (id,))
        con.commit()
    finally:
        con.close()
    return redirect("/admin")

if __name__=="__main__":
    if not os.path.exists(DB): init_db()
    app.run(debug=True)

# create_admin.py
import sqlite3, hashlib
from app import DB

username = "admin"
password = "yourpassword"   # CHANGE THIS

pw_hash = hashlib.sha256(password.encode()).hexdigest()

con = sqlite3.connect(DB)
con.execute("INSERT INTO users (username,password) VALUES (?,?)", (username, pw_hash))
con.commit()
con.close()

