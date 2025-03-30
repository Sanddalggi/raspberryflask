import sqlite3
import os

DB_PATH = 'users.db'

# 기존 DB 삭제 (선택 사항)
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

# DB 생성 및 테이블 초기화
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# users 테이블
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    password TEXT NOT NULL,
    qr_code TEXT
)
''')

# doorlocks 테이블
cursor.execute('''
CREATE TABLE doorlocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT NOT NULL
)
''')

# access_rights 테이블
cursor.execute('''
CREATE TABLE access_rights (
    user_id INTEGER,
    door_id INTEGER,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (door_id) REFERENCES doorlocks(id)
)
''')

# 테스트 사용자 추가 (정민, 수진)
cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", ("정민", "1234"))
cursor.execute("INSERT INTO users (name, password) VALUES (?, ?)", ("수진", "5678"))

# 테스트 도어락 추가 (301, 302)
cursor.execute("INSERT INTO doorlocks (location) VALUES (?)", ("301",))
cursor.execute("INSERT INTO doorlocks (location) VALUES (?)", ("302",))

# 접근 권한 추가: 정민 -> 301호, 수진 -> 302호
cursor.execute("INSERT INTO access_rights (user_id, door_id) VALUES (?, ?)", (1, 1))
cursor.execute("INSERT INTO access_rights (user_id, door_id) VALUES (?, ?)", (2, 2))

conn.commit()
conn.close()

print("✅ DB 초기화 및 사용자 정보 등록 완료!")
