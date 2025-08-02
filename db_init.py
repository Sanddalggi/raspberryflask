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
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    userid VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    email VARCHAR(100),
    doorid VARCHAR(100),
    qr_code TEXT,
    face_features TEXT,
    face_updated_at DATETIME,
    palm_features TEXT,
    palm_updated_at DATETIME,
    auth_method VARCHAR(50)
)
''')


cursor.execute("INSERT INTO users (username, userid, password, phone, email, doorid) VALUES (%s, %s, %s, %s, %s, %s)", ("정민", "jm1234", "1234", "010-1234-5678", "jm@example.com", "D402"))
cursor.execute("INSERT INTO users (username, userid, password, phone, email, doorid) VALUES (%s, %s, %s, %s, %s, %s)", ("범규", "bg5678", "5678", "010-9876-5432", "bg@example.com", "D403"))

conn.commit()
conn.close()
print("✅ MySQL DB 초기화 완료")