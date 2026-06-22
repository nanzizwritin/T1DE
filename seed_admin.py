import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

password = getpass("Set admin password: ")

conn = sqlite3.connect("diabetes.db")
cur = conn.cursor()

cur.execute("DELETE FROM users WHERE username = ?", ("admin",))
cur.execute(
    "INSERT INTO users (username, password_hash, role, center_id) VALUES (?, ?, ?, ?)",
    ("admin", generate_password_hash(password), "admin", None)
)

conn.commit()
conn.close()
print("Admin created.")