import os
#os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/opt/zbar/lib"  # M1/M2 Mac

import cv2
from pyzbar.pyzbar import decode
import requests
import time

SERVER_URL = "http://34.64.187.181:5000/check_qr"

def scan_qr_and_send(frame):
    qr_codes = decode(frame)
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        print(f"📷 QR 인식됨: {qr_data}")

        try:
            # 텍스트 형태로 서버에 전송 (폼 데이터 방식)
            response = requests.post(SERVER_URL, data={"qr_data": qr_data})
            print("🧠 서버 응답 코드:", response.status_code)
        except Exception as e:
            print(f"❌ 전송 오류 발생: {e}")

        time.sleep(3)  # 중복 방지용 딜레이

cap = cv2.VideoCapture(0)
print("✅ QR 스캔 시작 (ESC 누르면 종료)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    scan_qr_and_send(frame)

    cv2.imshow("QR Scanner", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()