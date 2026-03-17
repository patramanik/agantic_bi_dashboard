import sqlite3
import os

db_path = r"d:\Antygravaty\gfg\backend\app.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # Delete legacy chat logs that have no snapshot_id (not associated with any dataset)
    cursor.execute("DELETE FROM query_logs WHERE snapshot_id IS NULL;")
    conn.commit()
    print("Deleted legacy (orphaned) chat history.")
except sqlite3.OperationalError as e:
    print(f"Error: {e}")
finally:
    conn.close()
