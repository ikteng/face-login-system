import sqlite3
import cv2
from insightface.app import FaceAnalysis
import numpy as np
import os

DB = "face_db.sqlite"

# ------------------------------
# Prepare SQL database
# ------------------------------
def init_db():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            embedding BLOB
        )
    """)
    conn.commit()
    conn.close()


# ------------------------------
# Webcam capture
# ------------------------------
def capture_image():
    cap = cv2.VideoCapture(0)
    print("Press 'c' to capture, 'q' to quit.")

    while True:
        ret, frame = cap.read()
        cv2.imshow("Register User", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('c'):
            img = frame.copy()
            break
        elif key == ord('q'):
            img = None
            break

    cap.release()
    cv2.destroyAllWindows()
    return img


# ------------------------------
# Load InsightFace
# ------------------------------
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(640, 640))


# ------------------------------
# Main Registration Logic
# ------------------------------
init_db()

username = input("Enter username: ")
num_images = int(input("How many photos to capture? (recommended: 5–10) "))

conn = sqlite3.connect(DB)
cur = conn.cursor()

for i in range(num_images):
    print(f"\nCapture {i+1}/{num_images}")

    img = capture_image()
    if img is None:
        print("Cancelled.")
        break

    faces = app.get(img)
    if not faces:
        print("❌ No face detected — try again.")
        continue

    emb = faces[0].embedding.astype("float32")
    emb_bytes = emb.tobytes()

    cur.execute("INSERT INTO users (name, embedding) VALUES (?, ?)", (username, emb_bytes))
    conn.commit()

    print("✔ Saved embedding.")

conn.close()

print(f"\n🎉 Registration complete for user: {username}")
