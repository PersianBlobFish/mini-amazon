import sqlite3
con = sqlite3.connect("test.db")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY, name TEXT)")
cur.execute("INSERT INTO test (name) VALUES ('Sample Name')")
con.commit()
cur.execute("SELECT * FROM test")
rows = cur.fetchall()
for row in rows:
    print(row)