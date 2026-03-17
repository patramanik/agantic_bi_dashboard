import sqlite3
import os

db_path = r"d:\Antygravaty\gfg\backend\app.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE query_logs ADD COLUMN snapshot_id INTEGER REFERENCES data_snapshots(id);")
    conn.commit()
    print("Column 'snapshot_id' added successfully.")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e).lower():
        print("Column 'snapshot_id' already exists.")
    else:
        print(f"Error: {e}")
finally:
    conn.close()
