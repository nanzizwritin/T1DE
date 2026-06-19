import sqlite3

GLUCOSE_COLS = [
    "glucose_before_breakfast", "glucose_after_breakfast",
    "glucose_before_lunch",     "glucose_after_lunch",
    "glucose_before_dinner",    "glucose_after_dinner",
    "glucose_before_sleep",     "glucose_2_3_am",
]
INSULIN_COLS = [
    "insulin_before_breakfast", "insulin_before_lunch",
    "insulin_before_dinner",    "insulin_before_sleep",
    "insulin_2_3_am",
]

IN_LOW, IN_HIGH = 70, 180
HYPER = 200
HYPO  = 70


def num(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None          # skips "?", blanks, and junk


def analyse():
    conn = sqlite3.connect("diabetes.db")
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM readings").fetchall()
    conn.close()

    # ---------- GLUCOSE ----------
    total_days = len(rows)
    readings_monitored = 0
    readings_in_range  = 0
    days_in_range = 0
    hyper = 0
    hypo  = 0

    for row in rows:
        present = [num(row[c]) for c in GLUCOSE_COLS]
        present = [v for v in present if v is not None]

        readings_monitored += len(present)
        readings_in_range  += sum(1 for v in present if IN_LOW <= v <= IN_HIGH)
        hyper += sum(1 for v in present if v > HYPER)
        hypo  += sum(1 for v in present if v < HYPO)

        if present and all(IN_LOW <= v <= IN_HIGH for v in present):
            days_in_range += 1

    # ---------- INSULIN: days with < 4 readings ----------
    days_few_readings = 0
    for row in rows:
        present = [num(row[c]) for c in INSULIN_COLS]
        present = [v for v in present if v is not None]
        if len(present) < 4:
            days_few_readings += 1

    # ================= BASAL QUESTIONS GO HERE =================
    # After you confirm which column is the basal dose:
    #   (1) days with no basal dose
    #   (2) is basal changing by more than 2 units day to day
    # ==========================================================

    print("=== GLUCOSE ===")
    print("Total days monitored     :", total_days)
    print("Total readings monitored :", readings_monitored)
    print("Total days in range      :", days_in_range)
    print("Total readings in range  :", readings_in_range)
    print("Hyperglycaemic (>200)    :", hyper)
    print("Hypoglycaemic  (<70)     :", hypo)

    print("\n=== INSULIN ===")
    print("Days with < 4 readings   :", days_few_readings)


analyse()