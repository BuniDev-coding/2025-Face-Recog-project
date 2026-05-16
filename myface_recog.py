import cv2
from mtcnn import MTCNN
import datetime
import firebase_admin
from firebase_admin import credentials, firestore
import numpy as np
import face_recognition
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

# ---------- LINE Messaging API Configuration ----------
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')

def send_line_message(user_id, message):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {LINE_CHANNEL_ACCESS_TOKEN}'
    }
    payload = {
        'to': user_id,
        'messages': [{'type': 'text', 'text': message}]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print("LINE API response:", response.status_code, response.text)
        if response.status_code != 200:
            print(f"LINE Message API Error: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"Error sending LINE message: {e}")

# ---------- Firebase Initialization ----------
firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred = credentials.Certificate(firebase_cred_path)
try:
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit()

# ---------- Load Known Face Encodings ----------
known_face_encodings = {}
try:
    faces_ref = db.collection("faces")
    docs = faces_ref.get()
    for doc in docs:
        student_code = doc.id
        encoding = doc.to_dict().get("encoding")
        if encoding:
            known_face_encodings[student_code] = np.array(encoding)
except Exception as e:
    print(f"Error loading faces from Firestore: {e}")

# ---------- MTCNN Detector ----------
detector = MTCNN()

# ---------- Timestamp Formatter ----------
def format_timestamp(timestamp):
    try:
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Error formatting timestamp: {e}")
        return "N/A"

# ---------- Track Checked-in Students for Today ----------
checked_in_today = set()

# ---------- Video Capture ----------
video_capture = cv2.VideoCapture(0)

# ---------- Main Loop ----------
while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    faces = detector.detect_faces(rgb_frame)
    current_date = datetime.date.today().strftime("%Y-%m-%d")

    for face in faces:
        x, y, w, h = face["box"]
        face_encoding = face_recognition.face_encodings(rgb_frame, [(y, x + w, y + h, x)])

        name = "Unknown"
        if len(face_encoding) > 0:
            face_encoding = face_encoding[0]

            for student_code, known_encoding in known_face_encodings.items():
                try:
                    matches = face_recognition.compare_faces([known_encoding], face_encoding, tolerance=0.5)
                    face_distances = face_recognition.face_distance([known_encoding], face_encoding)

                    if matches[0] and face_distances[0] < 1:
                        name = student_code

                        if (student_code, current_date) in checked_in_today:
                            print(f"Already checked in today: {student_code}")
                            break

                        student_ref = db.collection("students").document(student_code)
                        student_data = student_ref.get().to_dict()

                        if student_data:
                            first_name = student_data.get("first_name", "")
                            last_name = student_data.get("last_name", "")
                            line_user_id = student_data.get("line_user_id")

                            now = datetime.datetime.now()
                            timestamp = now

                            attendance_data = {
                                "student_code": student_code,
                                "first_name": first_name,
                                "last_name": last_name,
                                "date": current_date,
                                "timestamp": firestore.SERVER_TIMESTAMP,
                                "status": "เข้าเรียน"
                            }

                            # Save to main collection "attendance"
                            db.collection("attendance").add(attendance_data)

                            # Save to main collection "attendance1"
                            db.collection("attendance1").add(attendance_data)

                            # Save to backup collection
                            try:
                                backup_doc_id = f"{student_code}_{timestamp.isoformat()}"
                                db.collection(f"attendance_backup/{current_date}").document(backup_doc_id).set(attendance_data)
                            except Exception as e:
                                print(f"Error backing up to Firestore: {e}")

                            formatted_time = format_timestamp(timestamp)
                            print(f"{first_name} {last_name} ({student_code}) เข้าเรียนเวลา {formatted_time}")
                            checked_in_today.add((student_code, current_date))

                            # === LINE Notification ===
                            if line_user_id:
                                print("ส่งแจ้งเตือนไปยัง LINE ID:", line_user_id)
                                line_message = f"✅ เช็คชื่อแล้ว: ({student_code}) เวลา {formatted_time}"
                                send_line_message(line_user_id, line_message)
                        break
                except Exception as e:
                    print(f"Error comparing faces: {e}")

        # Draw rectangle and name
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (x + 6, y + h - 6), font, 0.5, (255, 255, 255), 1)

    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# ---------- Cleanup ----------
video_capture.release()
cv2.destroyAllWindows()