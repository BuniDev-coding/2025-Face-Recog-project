import numpy as np

# โหลดไฟล์ face encoding ที่บันทึกไว้
encoding = np.load("student_002_encoding.npy")

print("✅ face encoding ที่โหลดได้:")
print(encoding)
print(f"ความยาวของ encoding: {len(encoding)} ค่า")