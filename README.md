# Face Recognition System

A Python-based face recognition system that uses MTCNN for face detection and `face_recognition` for generating encodings. It integrates with Firebase Firestore for storing face encodings and tracking student attendance, and uses the LINE Messaging API to send real-time notifications when a student checks in.

## Features

- **Real-time Face Detection**: Uses MTCNN for robust face detection in video streams.
- **Face Recognition**: Compares detected faces against known encodings using the `face_recognition` library.
- **Firebase Integration**: 
  - Retrieves known face encodings from Firestore.
  - Logs attendance data (check-in times) to Firestore (`attendance`, `attendance1`, and `attendance_backup` collections).
- **LINE Notifications**: Sends a LINE message to the student automatically upon successful check-in.
- **Encoding Generation Tool**: Includes scripts (`Mface_leaning.py` and `AI_learning.py`) to process videos, extract face encodings, and upload them to Firestore.

## Prerequisites

- Python 3.8+
- Webcam for real-time capturing
- Firebase project with Firestore database initialized
- LINE Channel Access Token for Messaging API

## Installation

1. **Clone or Download the Repository**

2. **Install Required Packages**
   ```bash
   pip install opencv-python mtcnn firebase-admin numpy face-recognition requests python-dotenv
   ```

3. **Firebase Configuration**
   - Obtain your Firebase Admin SDK private key JSON file.
   - Place the JSON file in the project directory (e.g., `facerecognitiondashboard-634e1-firebase-adminsdk-fbsvc-4d1d54408f.json`).

4. **Environment Variables**
   - Copy `.env.example` to `.env`.
   - Update the `.env` file with your LINE Channel Access Token and Firebase Credentials path.
   ```env
   LINE_CHANNEL_ACCESS_TOKEN=your_line_token_here
   FIREBASE_CREDENTIALS_PATH=facerecognitiondashboard-634e1-firebase-adminsdk-fbsvc-4d1d54408f.json
   ```

## Usage

### 1. Generating Encodings & Uploading to Firebase

- Run `Mface_leaning.py` to extract face encodings from a video file. This script saves the average encoding to a `.npy` file.
- Run `AI_learning.py` to upload an array of face encodings and associated student details to the Firebase `faces` collection.

### 2. Running the Main Face Recognition System

Start the real-time recognition script:
```bash
python myface_recog.py
```
- The camera will turn on and start detecting faces.
- Recognized students will have their attendance logged to Firebase.
- A LINE notification will be sent immediately upon successful check-in.
- Press `q` to quit the video window.

## Project Structure

- `myface_recog.py`: Main script for real-time face recognition and attendance logging.
- `AI_learning.py`: Helper script to upload face encodings to Firebase.
- `Mface_leaning.py`: Helper script to generate face encodings from a video stream.
- `Mface_convert.py`: Helper utility for face conversions.
- `.env`: Environment variables file (not included in version control).
# 2025-Project-Face-Recog
# 2025-Face-Recog-project
