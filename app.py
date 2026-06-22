import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "change-this-to-anything"

def db():
    conn = sqlite3.connect("diabetes.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")
    if session["role"] == "admin":
        return redirect("/admin")
    return f"Logged in as {session['username']} (nurse)"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        conn = db()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (request.form["username"],)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], request.form["password"]):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            return redirect("/")
        return render_template("login.html", error="Wrong username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin")
def admin():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    centers = conn.execute("SELECT * FROM centers").fetchall()
    nurses = conn.execute("SELECT * FROM users WHERE role = 'nurse'").fetchall()
    conn.close()
    return render_template("admin.html", centers=centers, nurses=nurses)

@app.route("/admin/add_center", methods=["POST"])
def add_center():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    conn.execute("INSERT INTO centers (name) VALUES (?)", (request.form["name"],))
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/add_nurse", methods=["POST"])
def add_nurse():
    if session.get("role") != "admin":
        return redirect("/login")
    center_id = request.form.get("center_id")
    if not center_id:
        return redirect("/admin")
    conn = db()
    conn.execute(
        "INSERT INTO users (username, password_hash, role, center_id) VALUES (?, ?, 'nurse', ?)",
        (request.form["username"], generate_password_hash(request.form["password"]), center_id)
    )
    conn.commit()
    conn.close()
    return redirect("/admin")

@app.route("/admin/data")
def admin_data():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    centers = conn.execute("SELECT * FROM centers").fetchall()

    selected_center = request.args.get("center")
    center = center_nurses = center_patients = None
    if selected_center:
        center = conn.execute("SELECT * FROM centers WHERE id=?", (selected_center,)).fetchone()
        center_nurses = conn.execute("SELECT * FROM users WHERE role='nurse' AND center_id=?", (selected_center,)).fetchall()
        center_patients = conn.execute("SELECT * FROM patients WHERE center_id=?", (selected_center,)).fetchall()
    conn.close()
    return render_template("data.html", centers=centers, center=center,
                           center_nurses=center_nurses, center_patients=center_patients,
                           selected_center=selected_center)
if __name__ == "__main__":
    app.run(debug=True)
