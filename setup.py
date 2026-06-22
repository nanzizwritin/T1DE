import sqlite3

conn = sqlite3.connect("diabetes.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS centers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password_hash TEXT,
    role TEXT,
    center_id INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id TEXT PRIMARY KEY,
    center_id INTEGER,
    name TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS readings (
    patient_id TEXT,
    date TEXT,
    glucose_before_breakfast   TEXT,
    glucose_after_breakfast    TEXT,
    glucose_before_lunch       TEXT,
    glucose_after_lunch        TEXT,
    glucose_before_dinner      TEXT,
    glucose_after_dinner       TEXT,
    glucose_before_sleep       TEXT,
    glucose_2_3_am             TEXT,
    insulin_before_breakfast   TEXT,
    insulin_before_lunch       TEXT,
    insulin_before_dinner      TEXT,
    insulin_before_sleep       TEXT,
    insulin_2_3_am             TEXT
)
""")

conn.commit()
conn.close()
print("Tables created: centers, users, patients, readings")