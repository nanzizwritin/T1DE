import sqlite3

def create_db(rec):
    data = rec
    conn = sqlite3.connect("diabetes.db")
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS readings (
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

    cur.execute("DELETE FROM readings")

    good_rows = []
    for row in data:
        if len(row) != 14:
            print("Bad row:", row)
        else:
            good_rows.append(row)

    cur.executemany("""
        INSERT INTO readings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, good_rows)

    conn.commit()
    conn.close()