from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import sqlite3
import os
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

DB_PATH = 'users.db'

# ------------------------- 로그인 기능 -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ? AND password = ?", (username, password))
        result = cursor.fetchone()
        conn.close()

        if result:
            session['user'] = username
            return redirect(url_for('generate_qr'))
        else:
            return "로그인 실패"

    return render_template('login.html')

# ------------------------- QR 생성 -------------------------
@app.route('/generate_qr')
def generate_qr():
    username = session.get('user')
    if not username:
        return redirect(url_for('login'))

    door_id = request.args.get('door', 'default')  # 도어락 ID 선택 방식 (기본값 있음)
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    qr_data = f"{username}_{door_id}_{timestamp}"

    import qrcode
    filename = f"{username}_{door_id}.png"
    filepath = os.path.join('static', 'qr_codes', filename)

    img = qrcode.make(qr_data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)

    # DB에 해당 사용자 QR 갱신
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET qr_code = ? WHERE name = ?", (qr_data, username))
    conn.commit()
    conn.close()

    return render_template('qr.html', username=username, filename=filename)

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

    # 사용자 인증 + 도어락 권한 확인
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = ?", (username,))
    user = cursor.fetchone()

    if not user:
        status = 'fail'
    else:
        user_id = user[0]
        # 접근 권한 확인
        cursor.execute("SELECT * FROM access_rights WHERE user_id = ? AND door_id = ?", (user_id, door_id))
        access = cursor.fetchone()

        if not access:
            status = 'fail'
        else:
            # QR 유효성 체크
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
    return render_template('qr.html', username=username, filename=filename)

# ------------------------- 기본 라우트 -------------------------
@app.route('/')
def index():
    return 'QR Server is running!'

# ------------------------- 서버 실행 -------------------------
if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=5000, debug=True)