import sqlite3
import cv2
from insightface.app import FaceAnalysis
import numpy as np

DB = "face_db.sqlite"

# ------------------------------
# Cosine similarity
# ------------------------------
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------------------------------
# Load InsightFace model
# ------------------------------
app = FaceAnalysis(name="buffalo_l")
app.prepare(ctx_id=0, det_size=(320, 320))

# ------------------------------
# Load database (group by username)
# ------------------------------
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT name, embedding FROM users")
rows = cur.fetchall()
conn.close()

user_embeddings = {}   # dict: name → list of embeddings

for name, emb_blob in rows:
    emb = np.frombuffer(emb_blob, dtype="float32")

    if name not in user_embeddings:
        user_embeddings[name] = []

    user_embeddings[name].append(emb)

print(f"Loaded {len(user_embeddings)} users from database.")
for u, embs in user_embeddings.items():
    print(f" → {u}: {len(embs)} embeddings")


# ------------------------------
# Real-time Recognition Loop
# ------------------------------
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open webcam.")
    exit()

print("Real-time face recognition running... Press 'q' to quit.")

SIM_THRESHOLD = 0.45

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    faces = app.get(frame)

    for face in faces:
        emb = face.embedding.astype("float32")

        best_score = -1
        best_name = "Unknown"

        # Compare against ALL stored embeddings
        for name, emb_list in user_embeddings.items():
            sims = [cosine_similarity(emb, db_emb) for db_emb in emb_list]
            user_best = max(sims)   # highest score among user's samples

            if user_best > best_score:
                best_score = user_best
                best_name = name

        # Apply threshold
        if best_score < SIM_THRESHOLD:
            best_name = "Unknown"

        # Draw box + label
        x1, y1, x2, y2 = face.bbox.astype(int)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        cv2.putText(frame, f"{best_name} ({best_score:.2f})",
                    (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                    (0, 255, 0), 2)

    cv2.imshow("Real-time Face Recognition", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
