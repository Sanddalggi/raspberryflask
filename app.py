from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
import sqlite3
import os
import secrets
import threading
import time
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

bycrypt = Bcrypt(app) # Bycrypt 인스턴스화
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

DB_PATH = 'users.db'
qr_generation_users = {}

# ------------------------- 로그인 기능 -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE name = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            cursor.execute("SELECT door_id FROM access_rights WHERE user_id = ?", (user_id,))
            door = cursor.fetchone()
            conn.close()

            if door:
                door_id = str(door[0])
                session['user'] = username
                qr_generation_users[username] = door_id

                # 로그인 즉시 QR 생성
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                qr_data = f"{username}_{door_id}_{timestamp}"
                print("🆕 로그인 후 QR 생성:", qr_data)

                filename = f"{username}_{door_id}.png"
                filepath = os.path.join('static', 'qr_codes', filename)

                img = qrcode.make(qr_data)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                img.save(filepath)

                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET qr_code = ? WHERE name = ?", (qr_data, username))
                conn.commit()
                conn.close()
                
                return redirect(url_for('show_qr', username=username))
            else:
                return "해당 사용자에게 연결된 도어락이 없습니다."
        else:
            return "로그인 실패"

    return render_template('login.html')

# ------------------------- QR 생성 루프 -------------------------
def generate_qr_loop():
    while True:
        for USERNAME, DOOR_ID in qr_generation_users.items():
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            qr_data = f"{USERNAME}_{DOOR_ID}_{timestamp}"
            print("🔁 QR 자동 생성:", qr_data)

            filename = f"{USERNAME}_{DOOR_ID}.png"
            filepath = os.path.join('static', 'qr_codes', filename)

            img = qrcode.make(qr_data)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            img.save(filepath)

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET qr_code = ? WHERE name = ?", (qr_data, USERNAME))
            conn.commit()
            conn.close()

        time.sleep(30)  # 30초마다 갱신

# ------------------------- QR 인증 -------------------------
@app.route('/check_qr', methods=['POST'])
def check_qr():
    data = request.get_json()
    qr_data = data.get('qr_data', '')

    try:
        username, door_id, timestamp = qr_data.split('_')
    except Exception as e:
        print(f"QR 파싱 오류: {e}")
        socketio.emit('qr_status', {'username': 'unknown', 'status': 'fail'})
        return jsonify({'status': 'fail'})

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user = cursor.fetchone()

    if not user:
        status = 'fail'
    else:
        user_id = user[0]
        cursor.execute("SELECT door_id FROM access_rights WHERE user_id = ?", (user_id,))
        door = cursor.fetchone()

        if not door:
            status = 'fail'
        else:
            actual_door_id = str(door[0])

            if door_id != actual_door_id:
                status = 'fail'
            else:
                cursor.execute("SELECT qr_code FROM users WHERE id = ?", (user_id,))
                result = cursor.fetchone()
                current_qr = result[0] if result else None
                if qr_data == current_qr:
                    status = 'success'
                else:
                    status = 'expired'

    conn.close()
    socketio.emit('qr_status', {'username': username, 'status': status})
    return jsonify({'status': status})

# ------------------------- QR 화면 -------------------------
@app.route('/qr/<username>')
def show_qr(username):
    qr_dir = os.path.join('static', 'qr_codes')
    filenames = [f for f in os.listdir(qr_dir) if f.startswith(username)]
    if not filenames:
        return "QR 코드가 존재하지 않습니다.", 404
    filename = filenames[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return render_template('qr.html', username=username, filename=filename, timestamp=timestamp)

# ------------------------- 기본 라우트 -------------------------
@app.route('/')
def index():
    return 'QR Server is running!'

# ------------------------- 서버 실행 -------------------------
if __name__ == '__main__':
    threading.Thread(target=generate_qr_loop, daemon=True).start()
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, use_reloader=False)
