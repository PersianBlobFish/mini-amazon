import sqlite3
con = sqlite3.connect("test.db")
cur = con.cursor()
# username = input("Enter username: ")
# password = input("Enter password: ")
# query = f"SELECT * FROM users WHERE name = '{username}' AND password = '{password }'"
# cur.execute(query)
# result = cur.fetchone()
# if result:
#     print("Login successful!")
# else:
#     print("Login failed!")
# con.close()
cmd = input("Enter command: ")
cur.execute(cmd)
con.commit()
con.close()