import time
import requests
import cv2
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
import numpy as np

SERVER_URL = "http://34.64.187.181:5000/check_qr"

# 카메라 초기화
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": "RGB888", "size": (640, 480)}))
picam2.start()
time.sleep(2)

def scan_qr_and_send(frame):
    qr_codes = decode(frame)
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        print(f"📷 QR 인식됨: {qr_data}")

        try:
            response = requests.post(SERVER_URL, data={"qr_data": qr_data})
            print("🧠 서버 응답 코드:", response.status_code)
        except Exception as e:
            print(f"❌ 전송 오류 발생: {e}")

        time.sleep(3)

print("✅ QR 스캔 시작 (Ctrl+C로 종료)")

try:
    while True:
        frame = picam2.capture_array()
        scan_qr_and_send(frame)

        cv2.imshow("QR Scanner", frame)
        if cv2.waitKey(1) & 0xFF == 27:  # ESC
            break
except KeyboardInterrupt:
    print("❎ 종료됨")

cv2.destroyAllWindows()
picam2.stop()