import sqlite3

# Connect to your SQLite database file
conn = sqlite3.connect("db.sqlite")
cursor = conn.cursor()

# Fetch all CREATE TABLE statements
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' ORDER BY name;")
rows = cursor.fetchall()

print("\n=== DATABASE SCHEMA ===\n")

for row in rows:
    if row[0] is not None:
        print(row[0])
        print()  # blank line between tables

conn.close()
