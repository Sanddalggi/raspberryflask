# qr_scanner.py
import os
os.environ["DYLD_LIBRARY_PATH"] = "/opt/homebrew/opt/zbar/lib"  # M1/M2
# os.environ["DYLD_LIBRARY_PATH"] = "/usr/local/opt/zbar/lib"   # Intel Mac

import cv2
from pyzbar.pyzbar import decode
import requests
import time
import webbrowser

SERVER_URL = "http://127.0.0.1:5000/check_qr"

def scan_qr_and_send(frame):
    qr_codes = decode(frame)
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        print(f"📷 QR 인식됨: {qr_data}")

        try:
            response = requests.post(SERVER_URL, json={"qr_data": qr_data})
            result = response.json()
            print("🧠 서버 응답:", result)
        except Exception as e:
            print(f"❌ 오류 발생: {e}")

        time.sleep(3)


cap = cv2.VideoCapture(0)
   

print("✅ QR 스캔 시작 (ESC 누르면 종료)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    scan_qr_and_send(frame)

    cv2.imshow("QR Scanner", frame)
    if cv2.waitKey(1) & 0xFF == 27:  # ESC로 종료
        break

cap.release()
cv2.destroyAllWindows()