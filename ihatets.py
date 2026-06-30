import sqlite3
from getpass import getpass
from werkzeug.security import generate_password_hash

pid = input("Patient ID: ")
pw = getpass("New password: ")

conn = sqlite3.connect("diabetes.db")
conn.execute("UPDATE patients SET password_hash=? WHERE patient_id=?",
             (generate_password_hash(pw), pid))
conn.commit()
conn.close()
print("Password reset.")