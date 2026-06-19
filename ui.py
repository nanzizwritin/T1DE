import sqlite3
import pandas as pd
import streamlit as st
def fix_readings():
    DB = "diabetes.db"

    st.title("Review readings")
    st.write("Click any cell to fix a ? or correct a wrong value, then Save.")

    conn = sqlite3.connect(DB)
    df = pd.read_sql("SELECT rowid AS _rid, * FROM readings", conn)
    conn.close()

    edited = st.data_editor(df, disabled=["_rid"], num_rows="fixed")

    if st.button("Save to database"):
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cols = [c for c in edited.columns if c != "_rid"]
        sets = ", ".join(f"{c} = ?" for c in cols)
        for _, row in edited.iterrows():
            values = [row[c] for c in cols] + [int(row["_rid"])]
            cur.execute(f"UPDATE readings SET {sets} WHERE rowid = ?", values)
        conn.commit()
        conn.close()
        st.success("Saved")