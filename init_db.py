import sqlite3

conn = sqlite3.connect("db.sqlite")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER,
    group_id INTEGER,
    expire_at TEXT
)
""")

conn.commit()
conn.close()
print("База готова!")