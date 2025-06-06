import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='uncledrew',
    password='',
    database='doorlock_db'
)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS access_rights")
cursor.execute("DROP TABLE IF EXISTS doorlocks")
cursor.execute("DROP TABLE IF EXISTS users")

cursor.execute('''
CREATE TABLE users (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    qr_code TEXT
)
''')


cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("정민", "1234"))
cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("범규", "5678"))

conn.commit()
conn.close()
print("✅ MySQL DB 초기화 완료")