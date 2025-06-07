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
# ------------------------- DB 연결 함수 -------------------------
def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='uncledrew',
        password='',
        database='doorlock_db'
    )

# ------------------------- 기본 라우트 -------------------------
@app.route('/')
def index():
    return '기본 라우트의 실행 화면이니 화면이 허전해도 걱정하지마쇼'

# ------------------------- 로그인 -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, password, doorid FROM users WHERE userid = %s", (userid,))
        user = cursor.fetchone()

        if user:
            user_id, username, hashed_pw, door_id = user
            if bcrypt.check_password_hash(hashed_pw, password):
                if door_id:
                    # ✅ 세션 등록
                    session['user'] = userid

                    # ✅ QR 자동 생성 루프 제외: 로그인 시 QR 생성하지 않음

                    conn.close()
                    return redirect(url_for('main'))
                else:
                    conn.close()
                    return "해당 사용자에게 연결된 도어락이 없습니다."
            else:
                conn.close()
                return "아이디 또는 비밀번호가 올바르지 않습니다."
        else:
            conn.close()
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
        doorid = request.form.get('doorid', '')

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE userid = %s", (userid,))
        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "이미 존재하는 사용자입니다."

        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')

        cursor.execute("INSERT INTO users (username, userid, password, phone, email, doorid) VALUES (%s, %s, %s, %s, %s, %s)",
                       (username, userid, hashed_pw, phone, email, doorid))
        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html')

# ------------------------- 인증 방식 선택 -------------------------
@app.route('/select_auth', methods=["GET"])
def select_auth():
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

# ------------------------- Main -------------------------
@app.route('/main')
def main():
    if "user" not in session:
        return redirect(url_for('login'))

    userid = session['user']
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT username, userid, doorid, phone, email FROM users WHERE userid = %s", (userid,))
    user = cursor.fetchone()
    conn.close()

    return render_template('main.html', user=user, username=user['username'])

# # ------------------------- QR 생성 루프 -------------------------
# def generate_qr_loop():
#     while True:
#         for userid, door_id in qr_generation_users.items():
#             timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#             qr_data = f"{userid}_{door_id}_{timestamp}"
#             print(f"[QR 재생성] {qr_data}")

#             # 파일 저장 경로
#             qr_dir = os.path.join('static', 'qr_codes')
#             os.makedirs(qr_dir, exist_ok=True)

#             # ✅ 기존 QR 파일 삭제 (userid로 시작하는 모든 파일)
#             for f in os.listdir(qr_dir):
#                 if f.startswith(f"{userid}_") and f.endswith(".png"):
#                     try:
#                         os.remove(os.path.join(qr_dir, f))
#                         print(f"삭제된 이전 QR 파일: {f}")
#                     except Exception as e:
#                         print(f"파일 삭제 오류: {f}, {e}")

#             # ✅ 새 QR 생성
#             filename = f"{userid}_{door_id}_{timestamp}.png"
#             filepath = os.path.join(qr_dir, filename)

#             img = qrcode.make(qr_data)
#             img.save(filepath)

#             # ✅ DB에 현재 QR 정보 저장
#             conn = get_db_connection()
#             cursor = conn.cursor()
#             cursor.execute("UPDATE users SET qr_code = %s WHERE userid = %s", (qr_data, userid))
#             conn.commit()
#             conn.close()

#         time.sleep(30)

#------------------------- QR 생성 -------------------------
@app.route('/generate_qr')
def generate_qr():
    userid = request.args.get('userid')
    if not userid:
        return jsonify({'status': 'fail', 'reason': 'No userid provided'})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doorid FROM users WHERE userid = %s", (userid,))
    result = cursor.fetchone()
    if not result:
        conn.close()
        return jsonify({'status': 'fail', 'reason': 'User not found'})

    doorid = result[0]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    qr_data = f"{userid}_{doorid}_{timestamp}"
    filename = f"{userid}_{doorid}_{timestamp}.png"
    qr_dir = os.path.join('static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)

    # 기존 파일 삭제
    for f in os.listdir(qr_dir):
        if f.startswith(f"{userid}_") and f.endswith(".png"):
            try:
                os.remove(os.path.join(qr_dir, f))
            except:
                pass

    filepath = os.path.join(qr_dir, filename)
    img = qrcode.make(qr_data)
    img.save(filepath)

    cursor.execute("UPDATE users SET qr_code = %s WHERE userid = %s", (qr_data, userid))
    conn.commit()
    conn.close()

    return jsonify({'status': 'ok', 'filename': filename})
# ------------------------- QR 인증 -------------------------
@app.route('/check_qr', methods=['POST'])
def check_qr():
    qr_data = request.form.get('qr_data', '')

    try:
        username, door_id, timestamp = qr_data.split('_')
        qr_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
    except Exception as e:
        print(f"QR 파싱 오류: {e}, 입력 데이터: {qr_data}")
        socketio.emit('qr_status', {'username': 'unknown', 'status': 'fail'})
        return jsonify({'status': 'fail'})

    # 유효시간 검사 (30초 이내만 허용)
    now = datetime.now()
    if (now - qr_time).total_seconds() > 30:
        socketio.emit('qr_status', {'username': username, 'status': 'expired'})
        return jsonify({'status': 'expired'})

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doorid, qr_code FROM users WHERE userid = %s", (username,))
    result = cursor.fetchone()

    if not result:
        status = 'fail'
    else:
        actual_door_id, current_qr = result

        if door_id != actual_door_id:
            status = 'fail'
        elif qr_data == current_qr:
            status = 'success'
        else:
            status = 'fail'  # QR 일치하지 않으면 실패로 간주

    conn.close()
    socketio.emit('qr_status', {'username': username, 'status': status})
    return jsonify({'status': status})

# ------------------------- QR 화면 -------------------------
@app.route('/qr/<userid>')
def show_qr(userid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT doorid, username FROM users WHERE userid = %s", (userid,))
    result = cursor.fetchone()
    conn.close()

    if not result:
        return "사용자 정보를 찾을 수 없습니다.", 404

    doorid, username = result

    # 기존 파일 삭제
    qr_dir = os.path.join('static', 'qr_codes')
    os.makedirs(qr_dir, exist_ok=True)
    for f in os.listdir(qr_dir):
        if f.startswith(f"{userid}_") and f.endswith('.png'):
            os.remove(os.path.join(qr_dir, f))

    # 새 QR 생성
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    qr_data = f"{userid}_{doorid}_{timestamp}"
    filename = f"{userid}_{doorid}_{timestamp}.png"
    filepath = os.path.join(qr_dir, filename)
    img = qrcode.make(qr_data)
    img.save(filepath)

    # DB 업데이트
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET qr_code = %s WHERE userid = %s", (qr_data, userid))
    conn.commit()
    conn.close()

    return render_template('qr.html', username=username, userid=userid, doorid=doorid, timestamp=timestamp, filename=filename)
# ------------------------- 로그 -------------------------
@app.route('/logs')
def logs():
    if "user" not in session:
        return redirect(url_for('login'))

    userid = session['user']

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id FROM users WHERE userid = %s", (userid,))
    user = cursor.fetchone()
    if not user:
        return "사용자 정보를 찾을 수 없습니다."

    user_id = user["id"]
    cursor.execute("SELECT event_type, timestamp FROM logs WHERE userid = %s ORDER BY timestamp DESC", (userid,))
    log_entries = cursor.fetchall()

    conn.close()
    return render_template('logs.html', logs=log_entries)

# ------------------------- Upload data -------------------------
@app.route('/upload_face_data', methods=['POST'])
def upload_face_data():
    data = request.get_json()
    userid = data.get('userid')
    features = str(data.get('features'))  # 문자열로 변환
    timestamp = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET face_features = %s, face_updated_at = %s WHERE userid = %s",
        (features, timestamp, userid)
    )
    conn.commit()
    conn.close()

    return "얼굴 데이터 업데이트 완료", 200


@app.route('/upload_palm_data', methods=['POST'])
def upload_palm_data():
    data = request.get_json()
    userid = data.get('userid')
    features = str(data.get('features'))
    timestamp = datetime.now()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET palm_features = %s, palm_updated_at = %s WHERE userid = %s",
        (features, timestamp, userid)
    )
    conn.commit()
    conn.close()

    return "손바닥 데이터 업데이트 완료", 200

# ------------------------- 로그아웃 -------------------------
@app.route('/logout')
def logout():
    userid = session.get('user')
    session.clear()
    return redirect(url_for('login'))

# ------------------------- 서버 실행 -------------------------
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000, debug=True, use_reloader=False)
