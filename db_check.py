import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM users")
print("Users:", cursor.fetchall())

cursor.execute("SELECT * FROM doorlocks")
print("Doorlocks:", cursor.fetchall())

cursor.execute("SELECT * FROM access_rights")
print("Access rights:", cursor.fetchall())

conn.close()
