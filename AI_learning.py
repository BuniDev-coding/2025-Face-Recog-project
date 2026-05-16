import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

load_dotenv()

# ตั้งค่า Firebase Admin SDK
firebase_cred_path = os.getenv('FIREBASE_CREDENTIALS_PATH')
cred = credentials.Certificate(firebase_cred_path)

try:
    firebase_admin.initialize_app(cred)
    db = firestore.client()
except Exception as e:
    print(f"Error initializing Firebase: {e}")
    exit()

# สร้าง collection "faces" และอ้างอิงเอกสาร
faces_ref = db.collection("faces")

# ข้อมูล face encoding ตัวอย่าง (array 128 มิติ)
face_encoding = [
    
]

# เพิ่มข้อมูลลงใน collection "faces"
data = {
    "encoding": face_encoding,
    "student_code": "65008311",
    "first_name": "ศุภเศรษฐ์",
    "last_name": "เดชาชัยภัทร",
}

faces_ref.document("65008311").set(data)

print("Collection 'faces' created and data added successfully.")