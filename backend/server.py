import base64
import sqlite3
import cv2
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from insightface.app import FaceAnalysis
from fastapi.middleware.cors import CORSMiddleware

DB = "face_db.sqlite"

# -------------------------------
# Init DB
# -------------------------------
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

init_db()

# -------------------------------
# Load InsightFace
# -------------------------------
app_insight = FaceAnalysis(name="buffalo_l")
app_insight.prepare(ctx_id=0, det_size=(320, 320))

# -------------------------------
# FastAPI + CORS
# -------------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allow Vue frontend
    allow_credentials=True,
    allow_methods=["*"],        # <-- Allows OPTIONS requests
    allow_headers=["*"],
)

class RegisterData(BaseModel):
    username: str
    image: str


@app.post("/register")
def register_face(data: RegisterData):
    img_bytes = base64.b64decode(data.image.split(",")[1])
    np_arr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    faces = app_insight.get(img)
    if not faces:
        return {"message": "❌ No face detected. Try again."}

    emb = faces[0].embedding.astype("float32")
    emb_bytes = emb.tobytes()

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name, embedding) VALUES (?, ?)",
                (data.username, emb_bytes))
    conn.commit()
    conn.close()

    return {"message": "✔ Face saved!"}

@app.post("/recognize")
def recognize_face(data: RegisterData):
    if not data.image or "," not in data.image:
        return {"name": "Unknown", "score": 0.0, "face_box": None, "error": "No image provided"}

    try:
        img_bytes = base64.b64decode(data.image.split(",")[1])
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return {"name": "Unknown", "score": 0.0, "face_box": None, "error": "Failed to decode image"}
    except Exception as e:
        return {"name": "Unknown", "score": 0.0, "face_box": None, "error": str(e)}

    faces = app_insight.get(img)
    if not faces:
        return {"name": "Unknown", "score": 0.0, "face_box": None}

    face = faces[0]
    emb = face.embedding.astype("float32")
    box = face.bbox  # x1, y1, x2, y2

    face_box = {"x": int(box[0]), "y": int(box[1]), "width": int(box[2]-box[0]), "height": int(box[3]-box[1])}

    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name, embedding FROM users")
    rows = cur.fetchall()
    conn.close()

    best_name = "Unknown"
    best_score = 0.0
    threshold = 0.5

    for name, emb_blob in rows:
        db_emb = np.frombuffer(emb_blob, dtype="float32")
        score = np.dot(emb, db_emb) / (np.linalg.norm(emb) * np.linalg.norm(db_emb))
        if score > best_score:
            best_score = score
            best_name = name

    if best_score < threshold:
        best_name = "Unknown"

    return {"name": best_name, "score": float(best_score), "face_box": face_box}
