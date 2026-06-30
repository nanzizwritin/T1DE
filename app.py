import sqlite3
from flask import Flask, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os, json
from RecognitionOfData import extract_from_corners
from datetime import datetime

app = Flask(__name__)
app.secret_key = "change-this-to-anything"

def db():
    conn = sqlite3.connect("diabetes.db")
    conn.row_factory = sqlite3.Row
    return conn

def parse_date(raw):
    if not raw or raw == "?":
        return "?"
    s = str(raw).strip()
    for sep in ["-", ".", " ", "\\", "|", ":"]:
        s = s.replace(sep, "/")
    parts = [p for p in s.split("/") if p != ""]
    if len(parts) < 2:
        return "?"
    try:
        day, month = int(parts[0]), int(parts[1])
    except ValueError:
        return "?"
    year = datetime.now().year
    try:
        return datetime(year, month, day).strftime("%Y-%m-%d")
    except ValueError:
        return "?"

GLUCOSE_COLS = [
    "glucose_before_breakfast", "glucose_after_breakfast",
    "glucose_before_lunch", "glucose_after_lunch",
    "glucose_before_dinner", "glucose_after_dinner",
    "glucose_before_sleep", "glucose_2_3_am",
]
INSULIN_COLS = [
    "insulin_before_breakfast", "insulin_before_lunch",
    "insulin_before_dinner", "insulin_before_sleep", "insulin_2_3_am",
]
BASAL_COL = "insulin_before_sleep"
IN_LOW, IN_HIGH, HYPER, HYPO = 70, 180, 200, 70

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def analyse_rows(rows):
    readings_monitored = readings_in_range = days_in_range = hyper = hypo = 0
    for row in rows:
        present = [num(row[c]) for c in GLUCOSE_COLS]
        present = [v for v in present if v is not None]
        readings_monitored += len(present)
        readings_in_range  += sum(1 for v in present if IN_LOW <= v <= IN_HIGH)
        hyper += sum(1 for v in present if v > HYPER)
        hypo  += sum(1 for v in present if v < HYPO)
        if present and all(IN_LOW <= v <= IN_HIGH for v in present):
            days_in_range += 1

    days_few_readings = days_no_basal = 0
    for row in rows:
        present = [num(row[c]) for c in INSULIN_COLS]
        present = [v for v in present if v is not None]
        if len(present) < 4:
            days_few_readings += 1
        if num(row[BASAL_COL]) is None:
            days_no_basal += 1

    basal_jump = False
    prev = None
    for row in rows:
        b = num(row[BASAL_COL])
        if b is not None:
            if prev is not None and abs(b - prev) > 2:
                basal_jump = True
            prev = b

    return {
        "total_days": len(rows),
        "readings_monitored": readings_monitored,
        "readings_in_range": readings_in_range,
        "days_in_range": days_in_range,
        "hyper": hyper, "hypo": hypo,
        "days_few_readings": days_few_readings,
        "days_no_basal": days_no_basal,
        "basal_jump": basal_jump,
    }

@app.route("/")
def home():
    role = session.get("role")
    if role == "admin":
        return redirect("/admin")
    if role == "nurse":
        return redirect("/nurse")
    if role == "patient":
        return redirect("/patient")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        conn = db()

        # 1. check users (admin / nurse)
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            session["center_id"] = user["center_id"]
            conn.close()
            return redirect("/")

        # 2. otherwise check patients (by username)
        patient = conn.execute("SELECT * FROM patients WHERE username = ?", (username,)).fetchone()
        if patient and patient["password_hash"] and check_password_hash(patient["password_hash"], password):
            session.clear()
            session["patient_id"] = patient["patient_id"]
            session["username"] = patient["name"]
            session["role"] = "patient"
            conn.close()
            return redirect("/")

        conn.close()
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
    return render_template("admin.html")

@app.route("/admin/manage")
def admin_manage():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    centers = conn.execute("SELECT * FROM centers").fetchall()
    conn.close()
    return render_template("admin_manage.html", centers=centers)

@app.route("/admin/add_center", methods=["POST"])
def add_center():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    conn.execute("INSERT INTO centers (name) VALUES (?)", (request.form["name"],))
    conn.commit()
    conn.close()
    return redirect("/admin/manage")
@app.route("/admin/add_nurse", methods=["POST"])
def add_nurse():
    if session.get("role") != "admin":
        return redirect("/login")
    center_id = request.form.get("center_id")
    if not center_id:
        return redirect("/admin/manage")
    username = request.form["username"]
    conn = db()
    if conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone():
        conn.close()
        flash("That username already exists — pick another.")
        return redirect("/admin/manage")
    conn.execute("INSERT INTO users (username, password_hash, role, center_id) VALUES (?, ?, 'nurse', ?)",
                 (username, generate_password_hash(request.form["password"]), center_id))
    conn.commit()
    conn.close()
    return redirect("/admin/manage")

@app.route("/admin/add_patient", methods=["POST"])
def admin_add_patient():
    if session.get("role") != "admin":
        return redirect("/login")
    center_id = request.form.get("center_id")
    if not center_id:
        return redirect("/admin/manage")
    username = request.form["username"]
    conn = db()
    clash = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() \
         or conn.execute("SELECT 1 FROM patients WHERE username=?", (username,)).fetchone()
    if clash:
        conn.close()
        flash("That username is already taken — pick another.")
        return redirect("/admin/manage")
    conn.execute("INSERT INTO patients (center_id, name, username, password_hash) VALUES (?, ?, ?, ?)",
                 (center_id, request.form["name"], username,
                  generate_password_hash(request.form["password"])))
    conn.commit()
    conn.close()
    return redirect("/admin/manage")

@app.route("/admin/data")
def admin_data():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    centers = conn.execute("SELECT * FROM centers").fetchall()
    selected = request.args.get("center")
    blocks = []
    rows = centers if selected == "all" else \
           [c for c in centers if str(c["id"]) == selected] if selected else []
    for c in rows:
        n = conn.execute("SELECT * FROM users WHERE role='nurse' AND center_id=?", (c["id"],)).fetchall()
        p = conn.execute("SELECT * FROM patients WHERE center_id=?", (c["id"],)).fetchall()
        blocks.append((c, n, p))
    conn.close()
    return render_template("data.html", centers=centers, blocks=blocks, selected=selected)

@app.route("/nurse")
def nurse():
    if session.get("role") != "nurse":
        return redirect("/login")
    return render_template("nurse.html")

@app.route("/nurse/patients")
def nurse_patients():
    if session.get("role") != "nurse":
        return redirect("/login")
    conn = db()
    patients = conn.execute("SELECT * FROM patients WHERE center_id=?", (session["center_id"],)).fetchall()
    conn.close()
    return render_template("nurse_patients.html", patients=patients)

@app.route("/nurse/add_patient", methods=["POST"])
def add_patient():
    if session.get("role") != "nurse":
        return redirect("/login")
    username = request.form["username"]
    conn = db()
    clash = conn.execute("SELECT 1 FROM users WHERE username=?", (username,)).fetchone() \
         or conn.execute("SELECT 1 FROM patients WHERE username=?", (username,)).fetchone()
    if clash:
        conn.close()
        flash("That username is already taken — pick another.")
        return redirect("/nurse/patients")
    conn.execute("INSERT INTO patients (center_id, name, username, password_hash) VALUES (?, ?, ?, ?)",
                 (session["center_id"], request.form["name"], username,
                  generate_password_hash(request.form["password"])))
    conn.commit()
    conn.close()
    return redirect("/nurse/patients")

@app.route("/nurse/patient/<int:pid>")
def nurse_patient(pid):
    if session.get("role") != "nurse":
        return redirect("/login")
    conn = db()
    patient = conn.execute(
        "SELECT * FROM patients WHERE patient_id=? AND center_id=?",
        (pid, session["center_id"])).fetchone()
    conn.close()
    if not patient:
        return redirect("/nurse")
    return render_template("patient.html", patient=patient)


@app.route("/nurse/save/<int:pid>", methods=["POST"])
def nurse_save(pid):
    if session.get("role") != "nurse":
        return redirect("/login")

    record = []
    for r in range(16):
        row = [request.form.get(f"cell_{r}_{c}", "").strip() for c in range(14)]
        record.append(row)

    def has_data(row):
        return any(cell not in ("", "?") for cell in row)
    filled = [row for row in record if has_data(row)]

    for row in filled:
        if row[0] in ("", "?"):
            flash("Every row with data needs a valid date.")
            return render_template("review.html", record=record, pid=pid)

    conn = db()
    for row in filled:
        conn.execute("""
            INSERT INTO readings (
                patient_id, center_id, entered_by, date,
                glucose_before_breakfast, glucose_after_breakfast,
                glucose_before_lunch, glucose_after_lunch,
                glucose_before_dinner, glucose_after_dinner,
                glucose_before_sleep, glucose_2_3_am,
                insulin_before_breakfast, insulin_before_lunch,
                insulin_before_dinner, insulin_before_sleep,
                insulin_2_3_am
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, [pid, session["center_id"], session["user_id"]] + row)
    conn.commit()
    conn.close()
    flash(f"Saved {len(filled)} rows for patient {pid}.")
    return redirect(f"/nurse/patient/{pid}")

@app.route("/admin/records")
def admin_records():
    if session.get("role") != "admin":
        return redirect("/login")
    conn = db()
    centers  = conn.execute("SELECT * FROM centers").fetchall()
    nurses   = conn.execute("SELECT * FROM users WHERE role='nurse'").fetchall()
    patients = conn.execute("SELECT * FROM patients").fetchall()

    center  = request.args.get("center")
    nurse   = request.args.get("nurse")
    patient = request.args.get("patient")

    query = "SELECT * FROM readings WHERE 1=1"
    params = []
    if center:
        query += " AND center_id = ?";  params.append(center)
    if nurse:
        query += " AND entered_by = ?";  params.append(nurse)
    if patient:
        query += " AND patient_id = ?";  params.append(patient)
    query += " ORDER BY date"

    readings = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("records.html",
        centers=centers, nurses=nurses, patients=patients,
        readings=readings, center=center, nurse=nurse, patient=patient)

@app.route("/analysis")
def analysis():
    if session.get("role") not in ("admin", "nurse"):
        return redirect("/login")
    role = session["role"]
    conn = db()
    centers = conn.execute("SELECT * FROM centers").fetchall()
    if role == "nurse":
        patients = conn.execute("SELECT * FROM patients WHERE center_id=?", (session["center_id"],)).fetchall()
    else:
        patients = conn.execute("SELECT * FROM patients").fetchall()

    start   = request.args.get("start")
    end     = request.args.get("end")
    patient = request.args.get("patient")
    center  = request.args.get("center")

    per_patient = None
    error = None

    if request.args.get("go"):
        if not start or not end:
            error = "Pick both a start and end date."
        else:
            query = "SELECT * FROM readings WHERE date BETWEEN ? AND ?"
            params = [start, end]
            if role == "nurse":
                query += " AND center_id = ?"; params.append(session["center_id"])
            elif center:
                query += " AND center_id = ?"; params.append(center)
            if patient:
                query += " AND patient_id = ?"; params.append(patient)
            query += " ORDER BY patient_id, date"
            rows = conn.execute(query, params).fetchall()

            names = {p["patient_id"]: p["name"] for p in patients}
            groups = {}
            for r in rows:
                groups.setdefault(r["patient_id"], []).append(r)
            per_patient = [(pid, names.get(pid, pid), analyse_rows(grp))
                           for pid, grp in groups.items()]

    conn.close()
    return render_template("analysis.html", role=role, centers=centers, patients=patients,
                           start=start, end=end, patient=patient, center=center,
                           per_patient=per_patient, error=error)

@app.route("/nurse/records")
def nurse_records():
    if session.get("role") != "nurse":
        return redirect("/login")
    conn = db()
    patients = conn.execute("SELECT * FROM patients WHERE center_id=?",
                            (session["center_id"],)).fetchall()
    patient = request.args.get("patient")

    query = "SELECT * FROM readings WHERE center_id = ?"
    params = [session["center_id"]]
    if patient:
        query += " AND patient_id = ?"; params.append(patient)
    query += " ORDER BY patient_id, date"

    readings = conn.execute(query, params).fetchall()
    conn.close()
    return render_template("nurse_records.html",
                           patients=patients, readings=readings, patient=patient)



@app.route("/nurse/corners/<int:pid>")
def nurse_corners(pid):
    if session.get("role") != "nurse":
        return redirect("/login")
    icols = request.args.get("icols", "5")
    return render_template("corners.html", pid=pid, icols=icols)

@app.route("/nurse/process/<int:pid>", methods=["POST"])
def nurse_process(pid):
    if session.get("role") != "nurse":
        return redirect("/login")
    corners = json.loads(request.form["corners"])
    icols = int(request.form.get("icols", 5))
    record = extract_from_corners("static/current.png", corners, insulin_cols=icols)
    for row in record:
        row[0] = parse_date(row[0])
    return render_template("review.html", record=record, pid=pid)

@app.route("/nurse/new/<int:pid>", methods=["GET", "POST"])
def nurse_new(pid):
    if session.get("role") != "nurse":
        return redirect("/login")
    if request.method == "POST":
        file = request.files.get("photo")
        if not file:
            return redirect(f"/nurse/new/{pid}")
        os.makedirs("static", exist_ok=True)
        file.save("static/current.png")

        from RecognitionOfData import check_image_quality
        problem = check_image_quality("static/current.png")
        if problem:
            flash(problem)
            return redirect(f"/nurse/new/{pid}")

        icols = request.form.get("insulin_cols", "5")
        return redirect(f"/nurse/corners/{pid}?icols={icols}")
    return render_template("new.html", pid=pid)

@app.route("/patient")
def patient_home():
    if session.get("role") != "patient":
        return redirect("/login")
    conn = db()
    readings = conn.execute(
        "SELECT * FROM readings WHERE patient_id = ? ORDER BY date",
        (session["patient_id"],)).fetchall()
    conn.close()
    return render_template("patient_portal.html", readings=readings)

if __name__ == "__main__":
    app.run(debug=True)