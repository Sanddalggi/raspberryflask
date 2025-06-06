from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from datetime import datetime
import mysql.connector
import os
import secrets
import threading
import time
import qrcode

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)

bcrypt = Bcrypt(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

qr_generation_users = {}

# ------------------------- DB 연결 함수 -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='doorlock_db'
    )

# ------------------------- 기본 라우트 -------------------------
@app.route('/')
def index():
    return '기본 라우트의 실행 화면이니 화면이 허전해도 걱정하지마쇼'

# ------------------------- 메인 페이지 -------------------------

@app.route('/main')
def main():

    return render_template('main.html')
# ------------------------- 로그인 -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE name = %s", (userid,))
        user = cursor.fetchone()
        conn.close()

        if user:
            user_id, hashed_pw = user
            if bcrypt.check_password_hash(hashed_pw, password):
                session['user'] = str(userid)
                generate_qr()
                return redirect(url_for('show_qr', username=userid))
            else:
                return "아이디 또는 비밀번호가 올바르지 않습니다."
        else:
            return "아이디 또는 비밀번호가 올바르지 않습니다."

    return render_template('login.html')

# ------------------------- 회원가입 -------------------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        userid = request.form['userid']
        password = request.form['password']
        phone = request.form['phone']
        email = request.form.get('email', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE name = %s", (userid,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "이미 존재하는 사용자입니다."

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        cursor.execute("INSERT INTO users (name, password, phone, email, realname) VALUES (%s, %s, %s, %s, %s)",
                       (userid, hashed_pw, phone, email, username))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# ------------------------- 인증 방식 선택 -------------------------
@app.route('/select_auth', methods=["GET"])
def select_auth_method():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("select_auth.html")

@app.route('/face_auth')
def face_auth():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('face_auth.html')

@app.route('/palm_auth')
def palm_auth():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('palm_auth.html')

# ------------------------- QR 생성 -------------------------
@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    if 'user' not in session:
        return redirect(url_for('login'))

    userid = str(session['user'])
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    qr_data = f"{userid}_{timestamp}"
    print("QR 코드 생성:", qr_data)

    filename = f"{userid}.png"
    filepath = os.path.join('static', 'qr_codes', filename)

    img = qrcode.make(qr_data)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    img.save(filepath)

    # DB에 저장
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET qr_code = %s WHERE name = %s", (qr_data, userid))
    conn.commit()
    conn.close()

    return redirect(url_for('show_qr', username=userid))


# ------------------------- QR 인증 -------------------------
@app.route('/check_qr', methods=['POST'])
def check_qr():
    data = request.get_json()
    qr_data = data.get('qr_data', '')

    try:
        username, timestamp = qr_data.split('_')
    except Exception as e:
        print(f"QR 파싱 오류: {e}")
        socketio.emit('qr_status', {'username': 'unknown', 'status': 'fail'})
        return jsonify({'status': 'fail'})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE name = %s", (username,))
    user = cursor.fetchone()

    if not user:
        status = 'fail'
    else:
        user_id = user[0]
        cursor.execute("SELECT qr_code FROM users WHERE id = %s", (user_id,))
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

# ------------------------- 서버 실행 -------------------------
if __name__ == '__main__':
    socketio.run(app, host="127.0.0.1", port=5000, debug=True, use_reloader=False)