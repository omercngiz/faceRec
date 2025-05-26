import cv2
import numpy as np
import insightface

from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity

class Recognizer:
    def __init__(self):
        # InsightFace modelini başlat
        self.face_app = insightface.app.FaceAnalysis(providers=['CPUExecutionProvider'])
        self.face_app.prepare(ctx_id=0, det_size=(640, 640))

        # Tanınmayan bir kişi için benzerlik eşik değeri
        self.similarity_threshold = 0.4

    def recognize_faces(self, frame, face_db):
        unknown_detected = False
        faces = self.face_app.get(frame)

        for face in faces:
            embedding = face.embedding
            name, age, gender, sim = self.find_match(embedding, face_db)

            # Koordinatlar
            x1, y1, x2, y2 = [int(v) for v in face.bbox]

            # Çerçeve çiz
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

            # Etiket yazısı
            label = f"{name}"
            if name != "Unknown":
                label += f" | {gender}, {age}"
            else:
                unknown_detected = True

            # Kutunun altına yaz
            cv2.putText(frame, label, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        return frame, unknown_detected

    def find_match(self, embedding, face_db):
        best_score = 0
        best_match = None

        embedding = np.array(embedding).reshape(1, -1)
        
        for person in face_db:
            db_embeddings = np.array(person["embeddings"])
            if db_embeddings.size == 0:
                continue
            scores = cosine_similarity(embedding, db_embeddings)
            max_score = np.max(scores)

            if max_score > best_score:
                best_score = max_score
                best_match = person

        if best_score >= self.similarity_threshold and best_match:
            return best_match["name"], best_match["age"], best_match["gender"], best_score
        else:
            return "Unknown", None, None, best_score
