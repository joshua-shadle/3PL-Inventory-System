import sqlite3

conn = sqlite3.connect("db.sqlite")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
tables = cursor.fetchall()

print("\n=== DATABASE CONTENTS ===\n")

for (table_name,) in tables:
    print(f"--- {table_name} ---")

    cursor.execute(f'SELECT * FROM "{table_name}"')
    rows = cursor.fetchall()

    if not rows:
        print("(no rows)\n")
        continue

    for row in rows:
        print(row)
    print()

conn.close()
