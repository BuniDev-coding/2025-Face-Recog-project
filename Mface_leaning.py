import cv2
import face_recognition
from mtcnn import MTCNN
import numpy as np
import os

# โหลด MTCNN detector
detector = MTCNN()

# เปิดวิดีโอ
video_capture = cv2.VideoCapture(r"C:\Users\WishISREAL\FaceRecog\Face\WIN_20250409_21_09_04_Pro.mp4")

if not video_capture.isOpened():
    print("❌ ไม่สามารถเปิดไฟล์วิดีโอได้")
    exit()

# ฟังก์ชันหมุนภาพตามองศาที่กำหนด
def rotate_frame(frame, angle):
    if angle == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    else:
        return frame  # ไม่หมุน

rotation_angle = 0  # เริ่มต้นไม่หมุน
encodings = []
max_encodings = 100

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    # หมุนเฟรมตามองศาที่กำหนด
    rotated_frame = rotate_frame(frame, rotation_angle)

    # แปลงเป็น RGB
    rgb_frame = cv2.cvtColor(rotated_frame, cv2.COLOR_BGR2RGB)

    # ตรวจจับใบหน้า
    faces = detector.detect_faces(rotated_frame)
    print(f"🧠 ตรวจพบใบหน้า {len(faces)} ใบ")

    for face in faces:
        x, y, w, h = face['box']
        confidence = face['confidence']

        if confidence < 0.95 or w < 60 or h < 60:
            continue

        x = max(0, x)
        y = max(0, y)
        x2 = min(x + w, rotated_frame.shape[1])
        y2 = min(y + h, rotated_frame.shape[0])

        top = y
        right = x + w
        bottom = y + h
        left = x

        try:
            face_encodings = face_recognition.face_encodings(rgb_frame, [(top, right, bottom, left)])

            if len(face_encodings) > 0:
                face_encoding = face_encodings[0]
                encodings.append(face_encoding)

                print(f"✅ บันทึก face encoding {len(encodings)}/{max_encodings}")
                cv2.rectangle(rotated_frame, (x, y), (x2, y2), (0, 255, 0), 2)

                if len(encodings) >= max_encodings:
                    break
            else:
                print("⚠️ ไม่พบ face encoding จากตำแหน่งนี้")

        except Exception as e:
            print(f"❌ เกิดข้อผิดพลาด: {e}")

    # แสดงวิดีโอ
    cv2.imshow('Video', rotated_frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('q') or len(encodings) >= max_encodings:
        break
    elif key == ord('r'):
        rotation_angle = (rotation_angle + 90) % 360
        print(f"🔄 หมุนวิดีโอไปที่ {rotation_angle} องศา")

video_capture.release()
cv2.destroyAllWindows()

# บันทึก face encoding เฉลี่ย
if len(encodings) > 0:
    mean_encoding = np.mean(encodings, axis=0)
    
    person_name = "student_002"
    save_path = f"{person_name}_encoding.npy"
    np.save(save_path, mean_encoding)

    print(f"\n💾 บันทึก face encoding ของ '{person_name}' แล้วที่: {save_path}")
else:
    print("❌ ไม่สามารถสร้าง encoding ได้")
video_capture.release()
cv2.destroyAllWindows()